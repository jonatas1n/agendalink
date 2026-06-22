from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .entitlements import subscription_snapshot
from .models import StoreSubscription


def require_store_subscription(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        snap = subscription_snapshot(request.user)
        if snap.can_manage_store:
            return view_func(request, *args, **kwargs)
        if snap.banner_message:
            messages.error(request, snap.banner_message)
        if (
            snap.subscription.status == StoreSubscription.STATUS_PAST_DUE
            and snap.subscription.pending_invoice_url
        ):
            return redirect("billing_subscribe")
        return redirect("billing_choose_plan")

    return _wrapped
