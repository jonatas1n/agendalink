from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def _to_decimal(value):
    if value is None or value == "":
        return None
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError):
        return None


def format_currency(value, *, symbol=False):
    """Format value as Brazilian currency (1.234,56)."""
    dec = _to_decimal(value)
    if dec is None:
        return ""
    dec = dec.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    negative = dec < 0
    dec = abs(dec)
    parts = f"{dec:.2f}".split(".")
    integer = int(parts[0])
    integer_fmt = f"{integer:,}".replace(",", ".")
    text = f"{integer_fmt},{parts[1]}"
    if negative:
        text = f"-{text}"
    if symbol:
        return f"R$ {text}"
    return text


def parse_currency_input(text):
    """Parse pt-BR text (1.234,56 or 50,00) to Decimal."""
    if text is None or text == "":
        return None
    if isinstance(text, Decimal):
        return text.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    raw = str(text).strip().replace("R$", "").replace(" ", "")
    if not raw:
        return None
    if "," in raw:
        raw = raw.replace(".", "").replace(",", ".")
    try:
        return Decimal(raw).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except (InvalidOperation, TypeError):
        return None
