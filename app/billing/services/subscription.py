import hashlib
import json
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from billing.asaas_client import (
    AsaasError,
    create_customer,
    create_subscription,
    list_subscription_payments,
)
from billing.cpf_cnpj import is_valid_cpf_cnpj, normalize_cpf_cnpj
from billing.models import AsaasWebhookEvent, BillingPlan, StoreSubscription
from billing.subscription_store import get_store_subscription


class SubscriptionServiceError(Exception):
    pass


def get_plan(slug: str) -> BillingPlan:
    try:
        return BillingPlan.objects.get(slug=slug, active=True)
    except BillingPlan.DoesNotExist as e:
        raise SubscriptionServiceError("Plano indisponível.") from e


def start_trial(user: User) -> StoreSubscription:
    plan = get_plan("trial_30")
    if plan.trial_days <= 0:
        raise SubscriptionServiceError("Trial indisponível.")

    with transaction.atomic():
        get_store_subscription(user)
        subscription = StoreSubscription.objects.select_for_update().get(user=user)
        if subscription.trial_used:
            raise SubscriptionServiceError(
                "Você já utilizou o período de teste gratuito."
            )
        if subscription.status not in (
            StoreSubscription.STATUS_PENDING,
            StoreSubscription.STATUS_CANCELED,
        ):
            raise SubscriptionServiceError(
                "Sua assinatura já está ativa ou em andamento."
            )

        now = timezone.now()
        subscription.plan = plan
        subscription.status = StoreSubscription.STATUS_TRIALING
        subscription.trial_used = True
        subscription.trial_ends_at = now + timedelta(days=plan.trial_days)
        subscription.delinquency_since = None
        subscription.pending_invoice_url = ""
        subscription.save()
    return subscription


def _display_name(user: User) -> str:
    full = user.get_full_name().strip()
    if full:
        return full
    return user.username


def start_paid_subscription(user: User, cpf_cnpj_raw: str) -> StoreSubscription:
    cpf_cnpj = normalize_cpf_cnpj(cpf_cnpj_raw)
    if not is_valid_cpf_cnpj(cpf_cnpj):
        raise SubscriptionServiceError("Informe um CPF ou CNPJ válido.")

    plan = get_plan("paid_monthly")
    if plan.price <= 0:
        raise SubscriptionServiceError("Plano pago não configurado.")

    with transaction.atomic():
        get_store_subscription(user)
        subscription = StoreSubscription.objects.select_for_update().get(user=user)
        if subscription.status == StoreSubscription.STATUS_ACTIVE:
            raise SubscriptionServiceError("Você já possui uma assinatura ativa.")

        subscription.plan = plan
        subscription.cpf_cnpj = cpf_cnpj
        subscription.status = StoreSubscription.STATUS_PENDING
        subscription.delinquency_since = None
        subscription.save(
            update_fields=[
                "plan",
                "cpf_cnpj",
                "status",
                "delinquency_since",
                "updated_at",
            ]
        )

    subscription = StoreSubscription.objects.get(user=user)
    try:
        if not subscription.asaas_customer_id:
            customer = create_customer(
                name=_display_name(user),
                email=user.email or f"{user.username}@local",
                cpf_cnpj=cpf_cnpj,
            )
            subscription.asaas_customer_id = customer.get("id") or ""
            subscription.save(update_fields=["asaas_customer_id", "updated_at"])

        next_due = timezone.localdate()
        sub_payload = create_subscription(
            customer_id=subscription.asaas_customer_id,
            value=plan.price,
            cycle=plan.asaas_cycle or "MONTHLY",
            next_due_date=next_due.isoformat(),
        )
        subscription.asaas_subscription_id = sub_payload.get("id") or ""
        subscription.pending_invoice_url = ""
        subscription.save(update_fields=["asaas_subscription_id", "updated_at"])

        invoice_url = _first_invoice_url(subscription.asaas_subscription_id)
        if invoice_url:
            subscription.pending_invoice_url = invoice_url
            subscription.save(update_fields=["pending_invoice_url", "updated_at"])
    except AsaasError as e:
        raise SubscriptionServiceError(str(e)) from e

    return subscription


def _first_invoice_url(subscription_id: str) -> str:
    if not subscription_id:
        return ""
    try:
        payments = list_subscription_payments(subscription_id)
    except AsaasError:
        return ""
    for payment in payments:
        url = payment.get("invoiceUrl") or payment.get("bankSlipUrl") or ""
        if url:
            return url
    return ""


def _event_key(payload: dict) -> str:
    event_id = payload.get("id")
    if event_id:
        return str(event_id)
    raw = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _find_subscription_for_payload(payload: dict) -> StoreSubscription | None:
    payment = payload.get("payment") or {}
    subscription_block = payload.get("subscription") or {}
    sub_id = subscription_block.get("id") or payment.get("subscription")
    customer_id = (payload.get("customer") or {}).get("id") or payment.get("customer")

    if sub_id:
        sub = StoreSubscription.objects.filter(asaas_subscription_id=sub_id).first()
        if sub:
            return sub
    if customer_id:
        return StoreSubscription.objects.filter(asaas_customer_id=customer_id).first()
    return None


def apply_asaas_webhook(payload: dict) -> bool:
    """Returns True if processed, False if duplicate."""
    key = _event_key(payload)
    if AsaasWebhookEvent.objects.filter(event_key=key).exists():
        return False

    event_type = (payload.get("event") or "").upper()
    subscription = _find_subscription_for_payload(payload)
    if not subscription:
        AsaasWebhookEvent.objects.create(event_key=key, event_type=event_type)
        return True

    now = timezone.now()
    paid_events = {
        "PAYMENT_RECEIVED",
        "PAYMENT_CONFIRMED",
        "PAYMENT_RECEIVED_IN_CASH",
    }
    overdue_events = {
        "PAYMENT_OVERDUE",
        "PAYMENT_DELETED",
    }
    canceled_events = {
        "SUBSCRIPTION_DELETED",
        "SUBSCRIPTION_INACTIVATED",
    }

    with transaction.atomic():
        AsaasWebhookEvent.objects.create(event_key=key, event_type=event_type)
        sub = StoreSubscription.objects.select_for_update().get(pk=subscription.pk)

        if event_type in paid_events:
            sub.status = StoreSubscription.STATUS_ACTIVE
            sub.delinquency_since = None
            sub.save(update_fields=["status", "delinquency_since", "updated_at"])
            return True

        if event_type in overdue_events:
            sub.status = StoreSubscription.STATUS_PAST_DUE
            if not sub.delinquency_since:
                sub.delinquency_since = now
            sub.save(update_fields=["status", "delinquency_since", "updated_at"])
            return True

        if event_type in canceled_events:
            sub.status = StoreSubscription.STATUS_CANCELED
            sub.save(update_fields=["status", "updated_at"])
            return True

    return True
