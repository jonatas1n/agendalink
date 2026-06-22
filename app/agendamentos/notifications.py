import logging
from datetime import datetime

from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone

logger = logging.getLogger(__name__)


def _from_email():
    return getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@agendalink.local")


def _format_starts_at_local(starts_at) -> str:
    if timezone.is_aware(starts_at):
        starts_at = timezone.localtime(starts_at)
    return starts_at.strftime("%d/%m/%Y às %H:%M")


def _owner_email(product):
    owner = product.owner
    if owner.email:
        return owner.email.strip()
    from core.store_profile import get_store_profile

    return (get_store_profile(owner).public_email or "").strip()


def _send_plain_email(*, subject: str, body: str, to: str) -> bool:
    if not to:
        return False
    try:
        EmailMessage(
            subject=subject,
            body=body,
            from_email=_from_email(),
            to=[to],
        ).send(fail_silently=False)
        return True
    except Exception as exc:
        logger.exception("Falha ao enviar e-mail (%s): %s", subject, exc)
        return False


def build_calendar_invite(appointment) -> str:
    starts = appointment.starts_at
    ends = appointment.ends_at
    if timezone.is_aware(starts):
        starts = timezone.localtime(starts)
    if timezone.is_aware(ends):
        ends = timezone.localtime(ends)

    def ics_dt(dt):
        return dt.strftime("%Y%m%dT%H%M%S")

    uid = f"appointment-{appointment.pk}@agendalink"
    product_name = appointment.product.name
    summary = f"Agendamento: {product_name}"
    description = (
        f"Serviço: {product_name}\\n" f"Cliente: {appointment.display_customer_name()}"
    )
    return "\r\n".join(
        [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//agendalink//PT",
            "CALSCALE:GREGORIAN",
            "METHOD:REQUEST",
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{ics_dt(datetime.now())}",
            f"DTSTART:{ics_dt(starts)}",
            f"DTEND:{ics_dt(ends)}",
            f"SUMMARY:{summary}",
            f"DESCRIPTION:{description}",
            "END:VEVENT",
            "END:VCALENDAR",
        ]
    )


def send_appointment_confirmation(appointment):
    sent_email = False
    sent_phone = False

    if appointment.confirm_via_email and appointment.recipient_email():
        sent_email = _send_confirmation_email(appointment)

    if appointment.confirm_via_phone and appointment.guest_phone:
        sent_phone = _send_confirmation_phone(appointment)

    return sent_email, sent_phone


def _send_confirmation_email(appointment) -> bool:
    to = appointment.recipient_email()
    if not to:
        return False
    product = appointment.product
    when = _format_starts_at_local(appointment.starts_at)
    subject = f"Confirmação de agendamento — {product.name}"
    body = (
        f"Olá, {appointment.display_customer_name()}!\n\n"
        f"Seu agendamento está confirmado.\n\n"
        f"Serviço: {product.name}\n"
        f"Data e horário: {when}\n\n"
        f"Em anexo está um convite de calendário (.ics) para você adicionar à agenda.\n\n"
        f"Enviaremos lembretes por e-mail antes do horário marcado.\n\n"
        f"Até lá!"
    )
    ics = build_calendar_invite(appointment)
    try:
        msg = EmailMessage(
            subject=subject,
            body=body,
            from_email=_from_email(),
            to=[to],
        )
        msg.attach(
            "agendamento.ics",
            ics,
            "text/calendar; method=REQUEST; charset=UTF-8",
        )
        msg.send(fail_silently=False)
        return True
    except Exception as exc:
        logger.exception("Falha ao enviar e-mail de confirmação: %s", exc)
        return False


def _send_confirmation_phone(appointment) -> bool:
    when = _format_starts_at_local(appointment.starts_at)
    message = (
        f"agendalink: agendamento confirmado — {appointment.product.name} "
        f"em {when}. Enviaremos lembretes antes do horário."
    )
    logger.info(
        "Confirmação por telefone (simulado) para %s: %s",
        appointment.guest_phone,
        message,
    )
    return True


def send_phone_confirmation_if_pending(appointment):
    if not appointment.confirm_via_phone or not appointment.guest_phone:
        return False
    return _send_confirmation_phone(appointment)


def send_new_booking_owner_notification(appointment) -> bool:
    owner_to = _owner_email(appointment.product)
    if not owner_to:
        return False
    when = _format_starts_at_local(appointment.starts_at)
    product_name = appointment.product.name
    subject = f"Novo agendamento — {product_name}"
    body = (
        f"Olá!\n\n"
        f"Você recebeu um novo agendamento.\n\n"
        f"Serviço: {product_name}\n"
        f"Cliente: {appointment.display_customer_name()}\n"
        f"E-mail: {appointment.display_guest_email()}\n"
        f"Telefone: {appointment.display_guest_phone()}\n"
        f"Data e horário: {when}\n\n"
        f"Acesse o painel do agendalink para ver detalhes."
    )
    return _send_plain_email(subject=subject, body=body, to=owner_to)


def send_cancellation_notifications(appointment, *, actor_user=None) -> dict:
    """Notifica cliente e, se o cancelamento não foi do profissional, o dono do serviço."""
    when = _format_starts_at_local(appointment.starts_at)
    product_name = appointment.product.name
    customer_name = appointment.display_customer_name()
    results = {"customer": False, "owner": False}

    customer_to = appointment.recipient_email()
    if customer_to:
        subject = f"Agendamento cancelado — {product_name}"
        body = (
            f"Olá, {customer_name}!\n\n"
            f"Seu agendamento foi cancelado.\n\n"
            f"Serviço: {product_name}\n"
            f"Horário: {when}\n\n"
            f"Se precisar remarcar, use o link de agendamento do profissional."
        )
        results["customer"] = _send_plain_email(
            subject=subject, body=body, to=customer_to
        )

    owner = appointment.product.owner
    actor_is_owner = actor_user is not None and actor_user.id == owner.id
    if not actor_is_owner:
        owner_to = _owner_email(appointment.product)
        if owner_to:
            subject = f"Agendamento cancelado — {product_name}"
            body = (
                f"Olá!\n\n"
                f"Um agendamento foi cancelado.\n\n"
                f"Serviço: {product_name}\n"
                f"Cliente: {customer_name}\n"
                f"Horário: {when}\n"
            )
            results["owner"] = _send_plain_email(
                subject=subject, body=body, to=owner_to
            )
    return results


def send_appointment_reminder(appointment, *, kind: str) -> bool:
    to = appointment.recipient_email()
    if not to or not appointment.confirm_via_email:
        return False
    when = _format_starts_at_local(appointment.starts_at)
    product_name = appointment.product.name
    if kind == "24h":
        subject = f"Lembrete: amanhã — {product_name}"
        lead = "Seu agendamento é amanhã."
    else:
        subject = f"Lembrete: em cerca de 1 hora — {product_name}"
        lead = "Seu agendamento começa em cerca de 1 hora."
    body = (
        f"Olá, {appointment.display_customer_name()}!\n\n"
        f"{lead}\n\n"
        f"Serviço: {product_name}\n"
        f"Data e horário: {when}\n\n"
        f"Até lá!"
    )
    return _send_plain_email(subject=subject, body=body, to=to)


def send_reschedule_suggestion(
    appointment,
    *,
    suggested_starts_at,
    book_url: str,
    message: str = "",
) -> bool:
    to_email = appointment.recipient_email()
    if not to_email:
        return False

    current_when = _format_starts_at_local(appointment.starts_at)
    suggested_when = _format_starts_at_local(suggested_starts_at)
    product_name = appointment.product.name
    subject = f"Sugestão de horário — {product_name}"
    extra = (
        f"\n\nMensagem do profissional:\n{message.strip()}\n" if message.strip() else ""
    )
    body = (
        f"Olá, {appointment.display_customer_name()}!\n\n"
        f"Sugerimos remarcar seu agendamento.\n\n"
        f"Serviço: {product_name}\n"
        f"Horário atual: {current_when}\n"
        f"Horário sugerido: {suggested_when}\n\n"
        f"Se este horário funcionar para você, confirme acessando o link de agendamento "
        f"e escolhendo o horário sugerido (ou outro disponível):\n{book_url}\n"
        f"{extra}\n"
        f"Até breve!"
    )
    return _send_plain_email(subject=subject, body=body, to=to_email)
