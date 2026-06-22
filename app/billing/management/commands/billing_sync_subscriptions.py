from django.core.management.base import BaseCommand

from billing.entitlements import sync_subscription_time_rules
from billing.models import StoreSubscription


class Command(BaseCommand):
    help = "Expira trials e promove inadimplência prolongada para bloqueado."

    def handle(self, *args, **options):
        updated = 0
        qs = StoreSubscription.objects.filter(
            status__in=[
                StoreSubscription.STATUS_TRIALING,
                StoreSubscription.STATUS_PAST_DUE,
            ],
        )
        for subscription in qs.iterator():
            if sync_subscription_time_rules(subscription):
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"Assinaturas atualizadas: {updated}"))
