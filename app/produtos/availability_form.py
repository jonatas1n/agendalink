from datetime import datetime

from django.core.exceptions import ValidationError


def _parse_date_value(value: str):
    value = (value or "").strip()
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    raise ValidationError(f"Data inválida: {value}")


def parse_unavailable_periods_post(post):
    starts = post.getlist("unavailable_start_date")
    ends = post.getlist("unavailable_end_date")
    reasons = post.getlist("unavailable_reason")
    periods = []
    for start_raw, end_raw, reason in zip(starts, ends, reasons):
        start_date = _parse_date_value(start_raw)
        if not start_date:
            continue
        end_date = _parse_date_value(end_raw) if (end_raw or "").strip() else start_date
        if end_date < start_date:
            raise ValidationError("A data final não pode ser anterior à inicial.")
        periods.append(
            {
                "start_date": start_date,
                "end_date": end_date,
                "reason": (reason or "").strip()[:200],
            }
        )
    return periods


def parse_date_availability_post(post):
    dates = post.getlist("exception_date")
    starts = post.getlist("exception_start_time")
    ends = post.getlist("exception_end_time")
    rows = []
    for date_raw, start, end in zip(dates, starts, ends):
        day = _parse_date_value(date_raw)
        if not day or not start or not end:
            continue
        if start >= end:
            raise ValidationError("O horário final deve ser depois do inicial.")
        rows.append(
            {
                "date": day,
                "start_time": start,
                "end_time": end,
            }
        )
    return rows
