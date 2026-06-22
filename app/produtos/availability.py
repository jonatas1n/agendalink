from datetime import date, datetime, timedelta

from agendamentos.models import Appointment
from produtos.models import (
    DateAvailability,
    DateBlock,
    Product,
    UnavailablePeriod,
    WeeklyAvailability,
)


def is_day_unavailable(product, day: date) -> bool:
    if DateBlock.objects.filter(product=product, date=day).exists():
        return True
    return UnavailablePeriod.objects.filter(
        product=product,
        start_date__lte=day,
        end_date__gte=day,
    ).exists()


def time_windows_for_day(product, day: date):
    """List of (start_time, end_time) for a day. Empty means no service."""
    if is_day_unavailable(product, day):
        return []

    exceptions = DateAvailability.objects.filter(product=product, date=day).order_by(
        "start_time"
    )
    if exceptions.exists():
        return [(e.start_time, e.end_time) for e in exceptions]

    weekly = WeeklyAvailability.objects.filter(
        product=product, weekday=day.weekday()
    ).order_by("start_time")
    return [(d.start_time, d.end_time) for d in weekly]


def available_slots_for_product(
    product: Product,
    days: int = 60,
    since: date | None = None,
    exclude_appointment_id: int | None = None,
):
    """Returns dict ISO date -> list of slots {start, end, available}."""
    since = since or date.today()
    slots_by_date = {}
    duration = timedelta(minutes=product.duration_minutes)

    for i in range(days):
        day = since + timedelta(days=i)
        windows = time_windows_for_day(product, day)
        slots = []

        for start_time, end_time in windows:
            cursor = datetime.combine(day, start_time)
            window_end = datetime.combine(day, end_time)

            while cursor + duration <= window_end:
                booking_qs = Appointment.objects.filter(
                    product=product,
                    starts_at=cursor,
                    status__in=["pendente", "confirmado"],
                )
                if exclude_appointment_id:
                    booking_qs = booking_qs.exclude(pk=exclude_appointment_id)
                booking_count = booking_qs.count()

                if booking_count < product.simultaneous_capacity:
                    slots.append(
                        {
                            "start": cursor.strftime("%H:%M"),
                            "end": (cursor + duration).strftime("%H:%M"),
                            "disponivel": True,
                            "available": True,
                        }
                    )
                cursor += duration

        if slots:
            slots_by_date[day.strftime("%Y-%m-%d")] = slots

    return slots_by_date


def is_starts_at_available_for_product(
    product: Product,
    starts_at: datetime,
    *,
    exclude_appointment_id: int | None = None,
) -> bool:
    from django.utils import timezone as tz

    if tz.is_aware(starts_at):
        local = tz.localtime(starts_at)
    else:
        local = starts_at
    day_key = local.date().strftime("%Y-%m-%d")
    start_label = local.strftime("%H:%M")
    slots_by_date = available_slots_for_product(
        product,
        days=60,
        since=local.date(),
        exclude_appointment_id=exclude_appointment_id,
    )
    return any(s["start"] == start_label for s in slots_by_date.get(day_key, []))
