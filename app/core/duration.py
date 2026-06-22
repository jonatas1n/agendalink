def format_duration_minutes(minutes):
    """Human-readable text for any duration in minutes."""
    if minutes is None:
        return ""
    try:
        total = int(minutes)
    except (TypeError, ValueError):
        return str(minutes)
    if total <= 0:
        return "0 min"
    hours, mins = divmod(total, 60)
    if hours and mins:
        return f"{hours}h {mins}min"
    if hours:
        return f"{hours}h"
    return f"{mins} min"


def duration_form_fields(minutes):
    """Split total minutes into hours and minutes for forms."""
    if minutes in (None, ""):
        return 0, 0
    try:
        total = int(minutes)
    except (TypeError, ValueError):
        return 0, 0
    return divmod(max(total, 0), 60)


def minutes_from_form_fields(hours, minutes):
    try:
        h = int(hours or 0)
        m = int(minutes or 0)
    except (TypeError, ValueError):
        return None
    if h < 0 or m < 0:
        return None
    if m >= 60:
        h += m // 60
        m = m % 60
    total = h * 60 + m
    return total if total > 0 else None
