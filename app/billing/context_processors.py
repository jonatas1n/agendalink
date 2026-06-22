from billing.models import StoreSubscription


def subscription_context(request):
    if not request.user.is_authenticated:
        return {}
    from billing.entitlements import subscription_snapshot

    snap = subscription_snapshot(request.user)
    status_labels = dict(StoreSubscription.STATUS_CHOICES)
    return {
        "subscription_snapshot": snap,
        "subscription_status_label": status_labels.get(
            snap.subscription.status, snap.subscription.status
        ),
    }
