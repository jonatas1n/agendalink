from django.http import JsonResponse
from django.views.decorators.http import require_GET
from core.currency import format_currency
from core.duration import format_duration_minutes
from core.json_response import json_error
from .models import Product
from .availability import available_slots_for_product


def serialize_product(product):
    prices = [
        {
            "duration_minutes": p.duration_minutes,
            "duration_label": (
                format_duration_minutes(p.duration_minutes)
                if p.duration_minutes
                else None
            ),
            "label": p.label,
            "variation_label": p.variation_label(),
            "price": str(p.price),
            "price_formatted": format_currency(p.price, symbol=True),
        }
        for p in product.prices.order_by("sort_order", "pk")
    ]
    if not prices:
        prices = [
            {
                "duration_minutes": product.duration_minutes,
                "duration_label": format_duration_minutes(product.duration_minutes),
                "label": "",
                "variation_label": product.duration_display(),
                "price": str(product.price),
                "price_formatted": format_currency(product.price, symbol=True),
            }
        ]
    return {
        "id": product.pk,
        "name": product.name,
        "description": product.description,
        "price_type": product.price_type,
        "price_criterion": product.price_criterion,
        "price_criterion_label": product.price_criterion_label,
        "criterion_label": product.criterion_display_label(),
        "price": str(product.price),
        "price_formatted": format_currency(product.price, symbol=True),
        "duration_minutes": product.duration_minutes,
        "prices": prices,
        "image": product.image.url if product.image else None,
    }


@require_GET
def list_products(request):
    products = Product.objects.filter(active=True)
    return JsonResponse({"products": [serialize_product(p) for p in products]})


@require_GET
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk, active=True)
        return JsonResponse(serialize_product(product))
    except Product.DoesNotExist:
        return json_error("Serviço não encontrado.", status=404)


@require_GET
def product_availability(request, pk):
    try:
        product = Product.objects.get(pk=pk, active=True)
    except Product.DoesNotExist:
        return json_error("Serviço não encontrado.", status=404)

    slots_by_date = available_slots_for_product(product, days=60)

    return JsonResponse(
        {
            "availability": slots_by_date,
            "product": serialize_product(product),
        }
    )
