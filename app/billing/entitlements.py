from dataclasses import dataclass
from datetime import timedelta

from django.conf import settings
from django.utils import timezone

from .models import StoreSubscription
from .subscription_store import get_store_subscription


@dataclass(frozen=True)
class SubscriptionSnapshot:
    subscription: StoreSubscription
    can_manage_store: bool
    banner_level: str | None
    banner_message: str | None


def _block_after_days() -> int:
    return int(getattr(settings, "BILLING_BLOCK_AFTER_DAYS", 15))


def _enforce_blocks() -> bool:
    return getattr(settings, "BILLING_ENFORCE_BLOCKS", True)


def _delinquency_days(subscription: StoreSubscription) -> int | None:
    if not subscription.delinquency_since:
        return None
    delta = timezone.now() - subscription.delinquency_since
    return max(0, delta.days)


def subscription_snapshot(user) -> SubscriptionSnapshot:
    subscription = get_store_subscription(user)
    sync_subscription_time_rules(subscription)
    subscription.refresh_from_db()
    status = subscription.status
    block_days = _block_after_days()
    delinq_days = _delinquency_days(subscription)

    if status == StoreSubscription.STATUS_PENDING:
        return SubscriptionSnapshot(
            subscription=subscription,
            can_manage_store=False,
            banner_level="info",
            banner_message="Escolha um plano para começar a usar o agendalink.",
        )

    if status == StoreSubscription.STATUS_TRIALING:
        days_left = None
        if subscription.trial_ends_at:
            days_left = (subscription.trial_ends_at - timezone.now()).days
        msg = "Período de teste ativo."
        if days_left is not None:
            if days_left < 0:
                msg = "Seu período de teste terminou. Assine para continuar."
            elif days_left == 0:
                msg = "Seu período de teste termina hoje."
            else:
                msg = f"Período de teste: {days_left} dia(s) restante(s)."
        return SubscriptionSnapshot(
            subscription=subscription,
            can_manage_store=True,
            banner_level="info",
            banner_message=msg,
        )

    if status == StoreSubscription.STATUS_ACTIVE:
        return SubscriptionSnapshot(
            subscription=subscription,
            can_manage_store=True,
            banner_level=None,
            banner_message=None,
        )

    if status == StoreSubscription.STATUS_PAST_DUE:
        blocked_by_time = delinq_days is not None and delinq_days >= block_days
        if blocked_by_time and _enforce_blocks():
            return SubscriptionSnapshot(
                subscription=subscription,
                can_manage_store=False,
                banner_level="error",
                banner_message=(
                    f"Pagamento em atraso há mais de {block_days} dias. "
                    "Regularize para voltar a editar serviços e horários."
                ),
            )
        msg = "Pagamento em atraso. Regularize sua assinatura para evitar bloqueio."
        if delinq_days is not None and _enforce_blocks():
            remaining = block_days - delinq_days
            if remaining > 0:
                msg = (
                    f"Pagamento em atraso. Em {remaining} dia(s) o acesso de edição "
                    "pode ser bloqueado."
                )
        return SubscriptionSnapshot(
            subscription=subscription,
            can_manage_store=True,
            banner_level="warning",
            banner_message=msg,
        )

    if status == StoreSubscription.STATUS_BLOCKED:
        if _enforce_blocks():
            return SubscriptionSnapshot(
                subscription=subscription,
                can_manage_store=False,
                banner_level="error",
                banner_message="Sua conta está bloqueada por inadimplência. Assine ou pague a fatura.",
            )
        return SubscriptionSnapshot(
            subscription=subscription,
            can_manage_store=True,
            banner_level="warning",
            banner_message="Sua conta está marcada como bloqueada. Regularize o pagamento.",
        )

    if status == StoreSubscription.STATUS_CANCELED:
        return SubscriptionSnapshot(
            subscription=subscription,
            can_manage_store=False,
            banner_level="warning",
            banner_message="Assinatura cancelada. Escolha um plano para reativar.",
        )

    return SubscriptionSnapshot(
        subscription=subscription,
        can_manage_store=False,
        banner_level="info",
        banner_message=None,
    )


def sync_subscription_time_rules(subscription: StoreSubscription) -> bool:
    """Apply trial expiry and past_due → blocked transitions. Returns True if saved."""
    now = timezone.now()
    changed = False
    block_days = _block_after_days()

    if (
        subscription.status == StoreSubscription.STATUS_TRIALING
        and subscription.trial_ends_at
        and subscription.trial_ends_at <= now
    ):
        subscription.status = StoreSubscription.STATUS_PAST_DUE
        if not subscription.delinquency_since:
            subscription.delinquency_since = subscription.trial_ends_at
        changed = True

    if (
        subscription.status == StoreSubscription.STATUS_PAST_DUE
        and subscription.delinquency_since
    ):
        if now - subscription.delinquency_since >= timedelta(days=block_days):
            subscription.status = StoreSubscription.STATUS_BLOCKED
            changed = True

    if changed:
        subscription.save(update_fields=["status", "delinquency_since", "updated_at"])
    return changed
