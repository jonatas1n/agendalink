from decimal import Decimal

from .prices import (
    apply_product_criterion,
    parse_criterion_post,
    parse_prices_post,
    save_prices,
    validate_prices,
)


def is_outros_post(post) -> bool:
    return (post.get("service_kind") or "agendamento").strip() == "outros"


def save_product_from_post(form, owner, post):
    """
    Persist product from ProductForm + POST. Returns (product, redirect_availability).
    Raises ValidationError for price rows when agendamento.
    """
    product = form.save(commit=False)
    product.owner = owner
    product.service_kind = form.cleaned_data.get("service_kind") or "agendamento"

    if product.is_outros():
        product.contact_channel = form.cleaned_data["contact_channel"]
        product.price = Decimal("0")
        product.price_type = "unico"
        product.price_criterion = "duracao"
        product.price_criterion_label = ""
        product.save()
        product.prices.all().delete()
        return product, False

    product.contact_channel = ""
    criterion, criterion_label = parse_criterion_post(post)
    parsed = validate_prices(parse_prices_post(post, criterion), criterion)
    apply_product_criterion(product, criterion, criterion_label)
    product.price = parsed[0]["price"]
    if parsed[0]["duration_minutes"] is not None:
        product.duration_minutes = parsed[0]["duration_minutes"]
    product.save()
    save_prices(product, parsed)
    return product, True
