from django.core.exceptions import ValidationError

from core.currency import format_currency, parse_currency_input
from core.duration import (
    duration_form_fields,
    format_duration_minutes,
    minutes_from_form_fields,
)
from .models import Product, ProductPrice

VALID_CRITERIA = {c[0] for c in Product.PRICE_CRITERION}
DEFAULT_DURATION_PRICE = 60
MIN_DURATION = 1
MAX_DURATION = 48 * 60

LABEL_PLACEHOLDERS = {
    "tipo": "Ex.: Consulta, Retorno, Avaliação…",
    "tamanho": "Ex.: P, M, G, Família…",
    "outros": "Descreva a opção…",
}


def _template_row(minutes, label="", price=""):
    hours, mins = duration_form_fields(minutes)
    return {
        "duration_minutes": minutes,
        "duration_h": hours,
        "duration_m": mins,
        "label": label,
        "price": price,
    }


def default_price_row(criterion="duracao"):
    minutes = DEFAULT_DURATION_PRICE if criterion == "duracao" else ""
    return _template_row(minutes, price="")


def criterion_for_template(product=None, post=None):
    if post is not None:
        criterion = (post.get("price_criterion") or "duracao").strip()
        if criterion not in VALID_CRITERIA:
            criterion = "duracao"
        return criterion, (post.get("price_criterion_label") or "").strip()
    if product is not None:
        return product.price_criterion, product.price_criterion_label
    return "duracao", ""


def prices_for_template(product=None, post=None):
    criterion, _ = criterion_for_template(product=product, post=post)
    if post is not None:
        return parse_prices_post(post, criterion)
    if product is not None:
        qs = product.prices.all()
        if qs.exists():
            return [
                _template_row(
                    p.duration_minutes if p.duration_minutes is not None else "",
                    p.label,
                    format_currency(p.price),
                )
                for p in qs
            ]
        return [
            _template_row(
                product.duration_minutes,
                "",
                format_currency(product.price),
            )
        ]
    return [default_price_row(criterion)]


def parse_criterion_post(post):
    criterion = (post.get("price_criterion") or "duracao").strip()
    if criterion not in VALID_CRITERIA:
        raise ValidationError("Selecione um critério de preço válido.")
    label = (post.get("price_criterion_label") or "").strip()
    if criterion == "outros" and not label:
        raise ValidationError(
            "Informe um nome para o critério (ex.: Pacote, Modalidade)."
        )
    if criterion != "outros":
        label = ""
    return criterion, label


def parse_prices_post(post, criterion="duracao"):
    hours = post.getlist("price_duration_hours")
    minutes_part = post.getlist("price_duration_minutes_part")
    labels = post.getlist("price_label")
    values = post.getlist("price_amount")
    rows = []
    for h_raw, m_raw, label_raw, value_raw in zip(hours, minutes_part, labels, values):
        label_raw = (label_raw or "").strip()
        value_raw = (value_raw or "").strip()
        duration = minutes_from_form_fields(h_raw, m_raw)
        if (duration is None or duration == 0) and not label_raw and not value_raw:
            continue
        rows.append(
            {
                "duration_minutes": duration,
                "label": label_raw,
                "price": value_raw,
            }
        )
    return rows or [default_price_row(criterion)]


def validate_prices(rows, criterion):
    if not rows:
        raise ValidationError("Informe pelo menos um preço.")

    parsed = []
    seen_keys = set()

    for i, row in enumerate(rows, start=1):
        value_raw = row.get("price")
        if value_raw in (None, ""):
            raise ValidationError(f"Linha {i}: informe o preço.")

        price = parse_currency_input(value_raw)
        if price is None:
            raise ValidationError(f"Linha {i}: preço inválido.")

        if price < 0:
            raise ValidationError(f"Linha {i}: o preço não pode ser negativo.")

        duration = row.get("duration_minutes")
        label = (row.get("label") or "").strip()

        if criterion == "duracao":
            if duration is None:
                raise ValidationError(
                    f"Linha {i}: informe a duração (horas e minutos)."
                )
            try:
                duration = int(duration)
            except (TypeError, ValueError):
                raise ValidationError(f"Linha {i}: duração inválida.")
            if duration < MIN_DURATION:
                raise ValidationError(
                    f"Linha {i}: a duração deve ser de pelo menos 1 minuto."
                )
            if duration > MAX_DURATION:
                raise ValidationError(f"Linha {i}: duração máxima de 48 horas.")
            label = format_duration_minutes(duration)
            key = duration
        else:
            duration = None
            if not label:
                raise ValidationError(f"Linha {i}: informe a opção.")
            if len(label) > 120:
                raise ValidationError(f"Linha {i}: texto da opção muito longo.")
            key = label.casefold()

        if key in seen_keys:
            raise ValidationError(
                "Não repita a mesma opção ou duração em mais de uma linha."
            )
        seen_keys.add(key)

        parsed.append(
            {
                "duration_minutes": duration,
                "label": label,
                "price": price,
            }
        )

    return parsed


def apply_product_criterion(product, criterion, criterion_label):
    product.price_criterion = criterion
    product.price_criterion_label = criterion_label if criterion == "outros" else ""


def save_prices(product, rows):
    product.prices.all().delete()
    for sort_order, row in enumerate(rows):
        ProductPrice.objects.create(
            product=product,
            duration_minutes=row["duration_minutes"],
            label=row["label"],
            price=row["price"],
            sort_order=sort_order,
        )
    product.sync_primary_price()
