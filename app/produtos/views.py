from urllib.parse import quote

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError

from billing.decorators import require_store_subscription

from .models import (
    DateAvailability,
    Product,
    UnavailablePeriod,
    WeeklyAvailability,
)
from core.store_profile import get_store_profile
from core.models import StoreProfile
from .availability_form import (
    parse_date_availability_post,
    parse_unavailable_periods_post,
)
from .forms import ProductForm
from .product_save import is_outros_post, save_product_from_post
from .prices import (
    LABEL_PLACEHOLDERS,
    criterion_for_template,
    parse_criterion_post,
    parse_prices_post,
    prices_for_template,
    validate_prices,
)


def _form_context(form, title, product=None, post=None, price_error=None):
    criterion, criterion_label = criterion_for_template(product=product, post=post)
    if post is not None:
        service_kind = (post.get("service_kind") or "agendamento").strip()
        contact_channel = (post.get("contact_channel") or "").strip()
    elif product is not None:
        service_kind = product.service_kind
        contact_channel = product.contact_channel
    else:
        service_kind = "agendamento"
        contact_channel = ""
    return {
        "form": form,
        "title": title,
        "product": product,
        "price_rows": prices_for_template(product=product, post=post),
        "price_criterion_choices": Product.PRICE_CRITERION,
        "price_criterion": criterion,
        "price_criterion_label": criterion_label,
        "label_placeholder": LABEL_PLACEHOLDERS,
        "price_error": price_error,
        "service_kind": service_kind,
        "contact_channel": contact_channel,
        "service_kind_choices": Product.SERVICE_KIND,
        "contact_channel_choices": Product.CONTACT_CHANNEL,
    }


def _parse_prices_from_post(post):
    criterion, criterion_label = parse_criterion_post(post)
    parsed = validate_prices(parse_prices_post(post, criterion), criterion)
    return criterion, criterion_label, parsed


def list_products(request):
    products = Product.objects.filter(active=True)
    return render(request, "produtos/lista.html", {"products": products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, active=True)
    weekly = product.weekly_availabilities.all()
    return render(
        request,
        "produtos/detalhe.html",
        {
            "product": product,
            "weekly_availabilities": weekly,
        },
    )


def _booking_page_context(request, product):
    user = request.user
    owner_products = (
        Product.objects.filter(owner=product.owner, active=True)
        .prefetch_related("prices")
        .order_by("name")
    )
    store = get_store_profile(product.owner)
    contact_phone_digits = ""
    if store.public_phone:
        contact_phone_digits = "".join(c for c in store.public_phone if c.isdigit())
    whatsapp_url = ""
    contact_channels_missing = False
    if product.is_outros():
        if product.contact_uses_whatsapp():
            if contact_phone_digits:
                msg = quote(f"Olá! Tenho interesse em {product.name}")
                whatsapp_url = f"https://wa.me/{contact_phone_digits}?text={msg}"
            else:
                contact_channels_missing = True
        if product.contact_uses_email() and not (store.public_email or "").strip():
            contact_channels_missing = True
    return {
        "product": product,
        "owner_products": owner_products,
        "store": store,
        "logged_in_user": user if user.is_authenticated else None,
        "whatsapp_url": whatsapp_url,
        "contact_channels_missing": contact_channels_missing,
    }


def book_product(request, pk):
    product = get_object_or_404(Product, pk=pk, active=True)
    return render(
        request,
        "produtos/agendar_conversa.html",
        _booking_page_context(request, product),
    )


def book_store_product(request, store_slug, pk):
    store = get_object_or_404(StoreProfile, slug=store_slug)
    product = get_object_or_404(Product, pk=pk, active=True, owner=store.user)
    return render(
        request,
        "produtos/agendar_conversa.html",
        _booking_page_context(request, product),
    )


@login_required
@require_store_subscription
def create_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        form.instance.owner = request.user
        price_error = None
        parsed_prices = None
        outros = is_outros_post(request.POST)
        if not outros:
            try:
                _criterion, _label, parsed_prices = _parse_prices_from_post(
                    request.POST
                )
            except ValidationError as e:
                price_error = e.messages[0]

        if form.is_valid() and (outros or parsed_prices is not None):
            try:
                product, to_availability = save_product_from_post(
                    form,
                    request.user,
                    request.POST,
                )
            except ValidationError as e:
                price_error = e.messages[0]
            else:
                messages.success(
                    request, f'Serviço "{product.name}" criado com sucesso!'
                )
                if to_availability:
                    return redirect("manage_availability", pk=product.pk)
                return redirect("dashboard")

        return render(
            request,
            "produtos/form.html",
            _form_context(
                form, "Novo serviço", post=request.POST, price_error=price_error
            ),
        )
    form = ProductForm()
    return render(request, "produtos/form.html", _form_context(form, "Novo serviço"))


@login_required
@require_store_subscription
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        price_error = None
        parsed_prices = None
        outros = is_outros_post(request.POST)
        if not outros:
            try:
                _criterion, _label, parsed_prices = _parse_prices_from_post(
                    request.POST
                )
            except ValidationError as e:
                price_error = e.messages[0]

        if form.is_valid() and (outros or parsed_prices is not None):
            try:
                save_product_from_post(form, request.user, request.POST)
            except ValidationError as e:
                price_error = e.messages[0]
            else:
                messages.success(request, "Serviço atualizado!")
                return redirect("dashboard")

        return render(
            request,
            "produtos/form.html",
            _form_context(
                form,
                "Editar serviço",
                product=product,
                post=request.POST,
                price_error=price_error,
            ),
        )
    form = ProductForm(instance=product)
    return render(
        request,
        "produtos/form.html",
        _form_context(form, "Editar serviço", product=product),
    )


@login_required
@require_store_subscription
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)
    if request.method == "POST":
        product.active = False
        product.save()
        messages.success(request, f'Serviço "{product.name}" removido.')
        return redirect("dashboard")
    return render(request, "produtos/confirmar_exclusao.html", {"product": product})


@login_required
@require_store_subscription
def manage_availability(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)
    if product.is_outros():
        messages.info(
            request, "Serviços do tipo Outros não usam horários de agendamento."
        )
        return redirect("dashboard")
    weekly = product.weekly_availabilities.all()
    unavailable_periods = product.unavailable_periods.all()
    date_availabilities = product.date_availabilities.all()

    if request.method == "POST":
        exception_error = None
        try:
            periods = parse_unavailable_periods_post(request.POST)
            date_rows = parse_date_availability_post(request.POST)
        except ValidationError as e:
            exception_error = e.messages[0] if e.messages else str(e)
            periods = None
            date_rows = None

        if exception_error:
            messages.error(request, exception_error)
        else:
            product.weekly_availabilities.all().delete()
            weekdays = request.POST.getlist("weekday")
            start_times = request.POST.getlist("start_time")
            end_times = request.POST.getlist("end_time")

            for weekday, start, end in zip(weekdays, start_times, end_times):
                if weekday and start and end:
                    WeeklyAvailability.objects.create(
                        product=product,
                        weekday=int(weekday),
                        start_time=start,
                        end_time=end,
                    )

            product.unavailable_periods.all().delete()
            for period in periods:
                UnavailablePeriod.objects.create(product=product, **period)

            product.date_availabilities.all().delete()
            for row in date_rows:
                DateAvailability.objects.create(product=product, **row)

            messages.success(request, "Disponibilidade salva com sucesso!")
            return redirect("dashboard")

        unavailable_periods = product.unavailable_periods.all()
        date_availabilities = product.date_availabilities.all()

    return render(
        request,
        "produtos/disponibilidade.html",
        {
            "product": product,
            "weekly_availabilities": weekly,
            "unavailable_periods": unavailable_periods,
            "date_availabilities": date_availabilities,
        },
    )
