from datetime import datetime

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from core.booking_link import booking_path_for_product
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from produtos.availability import (
    available_slots_for_product,
    is_starts_at_available_for_product,
)

from billing.decorators import require_store_subscription
from .models import Appointment
from .notifications import send_cancellation_notifications, send_reschedule_suggestion


def _appointments_for_user(user):
    return Appointment.objects.filter(
        Q(product__owner=user) | Q(customer=user),
    ).select_related("product", "customer")


def _redirect_after_appointment_action(request, default_view="list_appointments"):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
    ):
        return redirect(next_url)
    return redirect(default_view)


def _get_appointment_for_user(user, pk):
    return get_object_or_404(_appointments_for_user(user), pk=pk)


def _require_product_owner(user, appointment):
    if appointment.product.owner_id != user.id:
        raise Http404


@login_required
def list_appointments(request):
    appointments = _appointments_for_user(request.user).order_by("-starts_at")
    return render(request, "agendamentos/lista.html", {"appointments": appointments})


@login_required
def appointment_detail(request, pk):
    appointment = _get_appointment_for_user(request.user, pk)
    return render(request, "agendamentos/detalhe.html", {"appointment": appointment})


@login_required
def cancel_appointment(request, pk):
    appointment = _get_appointment_for_user(request.user, pk)
    if request.method == "POST":
        appointment.status = "cancelado"
        appointment.save()
        send_cancellation_notifications(appointment, actor_user=request.user)
        messages.success(request, "Agendamento cancelado.")
        return _redirect_after_appointment_action(request)
    return render(
        request,
        "agendamentos/confirmar_cancelamento.html",
        {"appointment": appointment},
    )


def _parse_starts_at(raw: str):
    raw = (raw or "").strip()
    if not raw:
        raise ValidationError("Escolha um horário sugerido.")
    try:
        starts_at = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ValidationError("Horário sugerido inválido.") from exc
    if timezone.is_naive(starts_at):
        starts_at = timezone.make_aware(starts_at)
    return starts_at


@login_required
@require_store_subscription
def suggest_reschedule(request, pk):
    appointment = get_object_or_404(
        _appointments_for_user(request.user).select_related("product"),
        pk=pk,
    )
    _require_product_owner(request.user, appointment)

    if appointment.status == "cancelado":
        messages.error(request, "Este agendamento já está cancelado.")
        return redirect("list_appointments")

    if not appointment.recipient_email():
        messages.error(
            request,
            "Não há e-mail do cliente para enviar a sugestão.",
        )
        return redirect("list_appointments")

    availability = available_slots_for_product(
        appointment.product,
        exclude_appointment_id=appointment.pk,
    )

    if request.method == "POST":
        try:
            suggested_starts_at = _parse_starts_at(request.POST.get("starts_at"))
        except ValidationError as e:
            messages.error(
                request,
                e.messages[0] if getattr(e, "messages", None) else str(e),
            )
            return redirect("suggest_reschedule", pk=pk)

        if not is_starts_at_available_for_product(
            appointment.product,
            suggested_starts_at,
            exclude_appointment_id=appointment.pk,
        ):
            messages.error(request, "O horário escolhido não está mais disponível.")
            return redirect("suggest_reschedule", pk=pk)

        book_url = request.build_absolute_uri(
            booking_path_for_product(appointment.product),
        )
        message = (request.POST.get("message") or "").strip()
        if send_reschedule_suggestion(
            appointment,
            suggested_starts_at=suggested_starts_at,
            book_url=book_url,
            message=message,
        ):
            messages.success(request, "Sugestão de horário enviada por e-mail.")
            return _redirect_after_appointment_action(request)

        messages.error(request, "Não foi possível enviar o e-mail. Tente novamente.")
        return redirect("suggest_reschedule", pk=pk)

    current_local = timezone.localtime(appointment.starts_at)
    return render(
        request,
        "agendamentos/suggest_reschedule.html",
        {
            "appointment": appointment,
            "availability": availability,
            "current_date_key": current_local.strftime("%Y-%m-%d"),
            "current_time_label": current_local.strftime("%H:%M"),
            "current_display": current_local.strftime("%d/%m/%Y às %H:%M"),
        },
    )
