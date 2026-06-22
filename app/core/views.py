from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms
import json

from django.urls import reverse

from billing.entitlements import subscription_snapshot
from billing.models import BillingPlan, StoreSubscription
from billing.subscription_store import get_store_subscription

from agendamentos.models import Appointment
from core.booking_link import resolve_booking_link
from core.forms import StoreSettingsForm
from core.models import StoreProfile
from core.store_profile import get_store_profile
from core.store_slug import RESERVED_STORE_SLUGS
from produtos.models import Product


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label="E-mail")
    first_name = forms.CharField(max_length=50, required=True, label="Nome")
    last_name = forms.CharField(max_length=50, required=True, label="Sobrenome")

    class Meta(UserCreationForm.Meta):
        fields = [
            "first_name",
            "last_name",
            "email",
            "username",
            "password1",
            "password2",
        ]
        error_messages = {
            "password_mismatch": "As senhas informadas não coincidem.",
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


def landing(request):
    return render(request, "landing/index.html")


def public_store(request, store_slug):
    profile = get_object_or_404(StoreProfile, slug=store_slug)
    products = (
        Product.objects.filter(owner=profile.user, active=True)
        .prefetch_related("prices")
        .order_by("name")
    )
    if products.count() == 1:
        product = products.first()
        return redirect("book_store_product", store_slug=profile.slug, pk=product.pk)
    return render(
        request,
        "core/public_store.html",
        {
            "store": profile,
            "products": products,
        },
    )


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request, f"Bem-vindo, {user.first_name}! Sua conta foi criada."
            )
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    snap = subscription_snapshot(request.user)
    if snap.subscription.status == StoreSubscription.STATUS_PENDING:
        return redirect("billing_choose_plan")

    appointments = (
        Appointment.objects.filter(
            Q(product__owner=request.user) | Q(customer=request.user),
        )
        .select_related("product", "customer")
        .order_by("-starts_at")[:10]
    )

    booking_link, booking_link_description = resolve_booking_link(request.user, request)

    return render(
        request,
        "dashboard/index.html",
        {
            "appointments": appointments,
            "booking_link": booking_link,
            "booking_link_description": booking_link_description,
        },
    )


@login_required
def store_settings(request):
    profile = get_store_profile(request.user)
    if request.method == "POST":
        form = StoreSettingsForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Definições da loja salvas.")
            return redirect("store_settings")
    else:
        form = StoreSettingsForm(instance=profile)
    return render(
        request,
        "dashboard/store_settings.html",
        {
            "form": form,
            "profile": profile,
            "subscription": get_store_subscription(request.user),
            "paid_plan": BillingPlan.objects.filter(
                slug="paid_monthly", active=True
            ).first(),
            "store_slug_validation_json": json.dumps(
                {
                    "reserved": sorted(RESERVED_STORE_SLUGS),
                    "checkUrl": reverse("api_check_store_slug"),
                }
            ),
        },
    )
