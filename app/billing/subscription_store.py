from .models import StoreSubscription


def get_store_subscription(user):
    subscription, _created = StoreSubscription.objects.get_or_create(user=user)
    return subscription
