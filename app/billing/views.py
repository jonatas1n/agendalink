from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from billing.forms import PaidSubscribeForm
from billing.models import BillingPlan, StoreSubscription
from billing.services.subscription import (
    SubscriptionServiceError,
    get_plan,
    start_paid_subscription,
    start_trial,
)
from billing.subscription_store import get_store_subscription


def _plans_context():
    trial = BillingPlan.objects.filter(slug="trial_30", active=True).first()
    paid = BillingPlan.objects.filter(slug="paid_monthly", active=True).first()
    return {"trial_plan": trial, "paid_plan": paid}


@login_required
def choose_plan(request):
    subscription = get_store_subscription(request.user)
    if subscription.status not in (
        StoreSubscription.STATUS_PENDING,
        StoreSubscription.STATUS_CANCELED,
    ):
        return redirect("dashboard")

    if request.method == "POST":
        choice = request.POST.get("plan")
        if choice == "trial":
            try:
                start_trial(request.user)
                messages.success(request, "Período de teste de 30 dias ativado!")
                return redirect("dashboard")
            except SubscriptionServiceError as e:
                messages.error(request, str(e))
        elif choice == "paid":
            return redirect("billing_subscribe")
        else:
            messages.error(request, "Escolha um plano válido.")

    return render(
        request,
        "billing/choose_plan.html",
        {
            **_plans_context(),
            "subscription": subscription,
        },
    )


@login_required
def subscribe(request):
    subscription = get_store_subscription(request.user)
    try:
        paid_plan = get_plan("paid_monthly")
    except SubscriptionServiceError:
        paid_plan = None

    if subscription.status == StoreSubscription.STATUS_ACTIVE:
        return redirect("store_settings")
    if (
        subscription.status == StoreSubscription.STATUS_TRIALING
        and request.method != "POST"
    ):
        messages.info(
            request, "Você está no trial. Ao assinar, a cobrança mensal passa a valer."
        )

    form = PaidSubscribeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            subscription = start_paid_subscription(
                request.user, form.cleaned_data["cpf_cnpj"]
            )
            messages.info(
                request,
                "Assinatura criada. Conclua o pagamento para ativar sua conta.",
            )
            if subscription.pending_invoice_url:
                return redirect(subscription.pending_invoice_url)
            return redirect("store_settings")
        except SubscriptionServiceError as e:
            messages.error(request, str(e))

    return render(
        request,
        "billing/subscribe.html",
        {
            "form": form,
            "paid_plan": paid_plan,
            "subscription": subscription,
        },
    )
