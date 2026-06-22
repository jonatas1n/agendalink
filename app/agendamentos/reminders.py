from datetime import timedelta

from django.utils import timezone

from .models import Appointment

ACTIVE_STATUSES = ("pendente", "confirmado")

# Janela em minutos ao redor do alvo (comando roda periodicamente, ex.: a cada 15 min).
REMINDER_24H_TARGET_MINUTES = 24 * 60
REMINDER_1H_TARGET_MINUTES = 60
REMINDER_WINDOW_MINUTES = 30


def _minutes_until(starts_at, now):
    return (starts_at - now).total_seconds() / 60


def _in_window(minutes_until, target_minutes):
    half = REMINDER_WINDOW_MINUTES / 2
    return (target_minutes - half) <= minutes_until <= (target_minutes + half)


def appointments_due_for_reminder(kind: str):
    now = timezone.now()
    flag_field = "reminder_24h_sent" if kind == "24h" else "reminder_1h_sent"
    target = (
        REMINDER_24H_TARGET_MINUTES if kind == "24h" else REMINDER_1H_TARGET_MINUTES
    )
    max_ahead = timedelta(hours=26)
    qs = Appointment.objects.filter(
        status__in=ACTIVE_STATUSES,
        starts_at__gt=now,
        starts_at__lte=now + max_ahead,
        **{flag_field: False},
    ).select_related("product", "product__owner", "customer")

    due = []
    for appointment in qs.iterator():
        minutes = _minutes_until(appointment.starts_at, now)
        if _in_window(minutes, target):
            due.append(appointment)
    return due
