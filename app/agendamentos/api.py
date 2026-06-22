import json
from datetime import datetime, timedelta

from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from core.currency import format_currency
from core.json_response import json_error
from produtos.models import Product
from .client_data import (
    normalize_phone,
    parse_client_payload,
    validate_client_for_booking,
)
from .models import Appointment
from .notifications import (
    send_appointment_confirmation,
    send_cancellation_notifications,
    send_new_booking_owner_notification,
    send_phone_confirmation_if_pending,
)


@require_GET
def check_availability(request):
    product_id = request.GET.get("product_id")
    starts_at_raw = request.GET.get("starts_at")

    if not product_id or not starts_at_raw:
        return json_error("Informe product_id e starts_at.")

    try:
        product = Product.objects.get(pk=product_id, active=True)
        starts_at = datetime.fromisoformat(starts_at_raw)
        ends_at = starts_at + timedelta(minutes=product.duration_minutes)
    except (Product.DoesNotExist, ValueError):
        return json_error("Dados inválidos.")

    count = Appointment.objects.filter(
        product=product,
        starts_at=starts_at,
        status__in=["pendente", "confirmado"],
    ).count()

    disponivel = count < product.simultaneous_capacity
    return JsonResponse(
        {
            "disponivel": disponivel,
            "available": disponivel,
            "capacidade_restante": product.simultaneous_capacity - count,
            "remaining_capacity": product.simultaneous_capacity - count,
            "starts_at": starts_at.isoformat(),
            "ends_at": ends_at.isoformat(),
        }
    )


def _create_appointment_record(product, starts_at, ends_at, client, user):
    return Appointment.objects.create(
        product=product,
        customer=user,
        starts_at=starts_at,
        ends_at=ends_at,
        notes="",
        guest_name=client["name"],
        guest_cpf=client["cpf"],
        guest_email=client["email"],
        guest_phone=client.get("phone") or "",
        confirm_via_email=True,
        confirm_via_phone=client["confirm_via_phone"],
        status="confirmado",
    )


@csrf_exempt
@require_POST
def create_appointment(request):
    try:
        data = json.loads(request.body)
        product_id = data.get("product_id")
        starts_at_raw = data.get("starts_at")
    except (json.JSONDecodeError, AttributeError):
        return json_error("JSON inválido.")

    if not product_id or not starts_at_raw:
        return json_error("Informe product_id e starts_at.")

    client = parse_client_payload(data)
    if not client:
        return json_error("Informe os dados do cliente (nome, CPF e e-mail).")

    try:
        client = validate_client_for_booking(client)
    except DjangoValidationError as e:
        return json_error(e.messages[0] if e.messages else str(e))

    try:
        product = Product.objects.get(pk=product_id, active=True)
        starts_at = datetime.fromisoformat(starts_at_raw)
        if timezone.is_naive(starts_at):
            starts_at = timezone.make_aware(starts_at)
        ends_at = starts_at + timedelta(minutes=product.duration_minutes)
    except (Product.DoesNotExist, ValueError):
        return json_error("Dados inválidos.")

    count = Appointment.objects.filter(
        product=product,
        starts_at=starts_at,
        status__in=["pendente", "confirmado"],
    ).count()

    if count >= product.simultaneous_capacity:
        return json_error("Horário indisponível.", status=409)

    user = request.user if request.user.is_authenticated else None
    appointment = _create_appointment_record(product, starts_at, ends_at, client, user)

    need_phone = appointment.confirm_via_phone and not appointment.guest_phone
    sent_email, sent_phone = send_appointment_confirmation(appointment)
    owner_notified = send_new_booking_owner_notification(appointment)

    return JsonResponse(
        {
            "id": appointment.pk,
            "product_name": product.name,
            "starts_at": starts_at.isoformat(),
            "ends_at": ends_at.isoformat(),
            "status": appointment.status,
            "needs_phone": need_phone,
            "email_confirmation_sent": sent_email,
            "phone_confirmation_sent": sent_phone,
            "owner_notification_sent": owner_notified,
        },
        status=201,
    )


@csrf_exempt
@require_POST
def update_appointment_phone(request, pk):
    try:
        data = json.loads(request.body)
        phone_raw = data.get("phone") or ""
    except (json.JSONDecodeError, AttributeError):
        return json_error("JSON inválido.")

    phone = normalize_phone(phone_raw)
    if len(phone) < 10:
        return json_error("Informe um telefone válido com DDD.")

    try:
        appointment = Appointment.objects.get(pk=pk)
    except Appointment.DoesNotExist:
        return json_error("Agendamento não encontrado.", status=404)

    appointment.guest_phone = phone
    appointment.save(update_fields=["guest_phone", "updated_at"])
    sent = send_phone_confirmation_if_pending(appointment)

    return JsonResponse(
        {
            "ok": True,
            "phone_confirmation_sent": sent,
        }
    )


@require_GET
def my_appointments(request):
    if not request.user.is_authenticated:
        return json_error("Faça login para continuar.", status=401)

    appointments = (
        Appointment.objects.filter(customer=request.user)
        .select_related("product")
        .order_by("-starts_at")[:20]
    )

    return JsonResponse(
        {
            "appointments": [
                {
                    "id": a.pk,
                    "product_name": a.product.name,
                    "starts_at": a.starts_at.isoformat(),
                    "ends_at": a.ends_at.isoformat(),
                    "status": a.status,
                    "amount_paid": str(a.amount_paid),
                    "amount_paid_formatted": (
                        format_currency(a.amount_paid, symbol=True)
                        if a.amount_paid is not None
                        else None
                    ),
                }
                for a in appointments
            ]
        }
    )


@csrf_exempt
@require_POST
def cancel_appointment(request, pk):
    if not request.user.is_authenticated:
        return json_error("Faça login para continuar.", status=401)

    try:
        appointment = Appointment.objects.get(pk=pk, customer=request.user)
    except Appointment.DoesNotExist:
        return json_error("Agendamento não encontrado.", status=404)

    if appointment.status == "cancelado":
        return json_error("Este agendamento já está cancelado.")

    appointment.status = "cancelado"
    appointment.save()
    send_cancellation_notifications(appointment, actor_user=request.user)
    return JsonResponse({"ok": True, "status": "cancelado"})
