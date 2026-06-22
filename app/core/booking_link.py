from django.urls import reverse

from core.store_profile import get_store_profile


def resolve_booking_link(user, request):
    """Public link to the professional's store (pretty URL by slug)."""
    from produtos.models import Product

    profile = get_store_profile(user)
    has_product = Product.objects.filter(owner=user, active=True).exists()
    if not has_product or not profile.slug:
        product = (
            Product.objects.filter(owner=user, active=True)
            .order_by("-created_at")
            .first()
        )
        if not product:
            return None, None
        url = request.build_absolute_uri(
            reverse("book_product", args=[product.pk]),
        )
        return url, f"Agendar {product.name}"

    url = request.build_absolute_uri(
        reverse("public_store", args=[profile.slug]),
    )
    label = profile.display_name or "Sua loja"
    return url, f"Agendar — {label}"


def booking_path_for_product(product):
    profile = get_store_profile(product.owner)
    if profile.slug:
        return reverse("book_store_product", args=[profile.slug, product.pk])
    return reverse("book_product", args=[product.pk])
