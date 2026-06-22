from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from billing.entitlements import subscription_snapshot, sync_subscription_time_rules
from billing.models import BillingPlan, StoreSubscription
from billing.services.subscription import apply_asaas_webhook, start_trial
from billing.subscription_store import get_store_subscription


class EntitlementsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="pro", password="pass", email="pro@test.com"
        )
        BillingPlan.objects.get_or_create(
            slug="trial_30",
            defaults={
                "name": "Trial",
                "price": Decimal("0"),
                "trial_days": 30,
                "active": True,
            },
        )

    def test_pending_cannot_manage_store(self):
        snap = subscription_snapshot(self.user)
        self.assertFalse(snap.can_manage_store)

    @override_settings(BILLING_ENFORCE_BLOCKS=True, BILLING_BLOCK_AFTER_DAYS=15)
    def test_past_due_blocks_after_grace(self):
        sub = get_store_subscription(self.user)
        sub.status = StoreSubscription.STATUS_PAST_DUE
        sub.delinquency_since = timezone.now() - timedelta(days=16)
        sub.save()
        snap = subscription_snapshot(self.user)
        self.assertFalse(snap.can_manage_store)

    @override_settings(BILLING_ENFORCE_BLOCKS=True, BILLING_BLOCK_AFTER_DAYS=15)
    def test_past_due_allows_manage_within_grace(self):
        sub = get_store_subscription(self.user)
        sub.status = StoreSubscription.STATUS_PAST_DUE
        sub.delinquency_since = timezone.now() - timedelta(days=3)
        sub.save()
        snap = subscription_snapshot(self.user)
        self.assertTrue(snap.can_manage_store)

    def test_trial_expiry_moves_to_past_due(self):
        sub = get_store_subscription(self.user)
        sub.status = StoreSubscription.STATUS_TRIALING
        sub.trial_ends_at = timezone.now() - timedelta(hours=1)
        sub.save()
        self.assertTrue(sync_subscription_time_rules(sub))
        sub.refresh_from_db()
        self.assertEqual(sub.status, StoreSubscription.STATUS_PAST_DUE)


class WebhookTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="pay", password="pass")
        self.sub = get_store_subscription(self.user)
        self.sub.asaas_customer_id = "cus_123"
        self.sub.asaas_subscription_id = "sub_456"
        self.sub.status = StoreSubscription.STATUS_PENDING
        self.sub.save()

    def test_payment_received_activates(self):
        payload = {
            "id": "evt_1",
            "event": "PAYMENT_RECEIVED",
            "payment": {"customer": "cus_123", "subscription": "sub_456"},
        }
        self.assertTrue(apply_asaas_webhook(payload))
        self.sub.refresh_from_db()
        self.assertEqual(self.sub.status, StoreSubscription.STATUS_ACTIVE)

    def test_webhook_idempotent(self):
        payload = {
            "id": "evt_dup",
            "event": "PAYMENT_RECEIVED",
            "payment": {"customer": "cus_123", "subscription": "sub_456"},
        }
        self.assertTrue(apply_asaas_webhook(payload))
        self.assertFalse(apply_asaas_webhook(payload))


class DashboardGateTests(TestCase):
    def test_pending_redirects_to_choose_plan(self):
        user = User.objects.create_user(username="new", password="pass")
        client = Client()
        client.login(username="new", password="pass")
        response = client.get(reverse("dashboard"))
        self.assertRedirects(response, reverse("billing_choose_plan"))

    def test_trial_allows_dashboard(self):
        user = User.objects.create_user(username="trial", password="pass")
        BillingPlan.objects.get_or_create(
            slug="trial_30",
            defaults={
                "name": "Trial",
                "price": Decimal("0"),
                "trial_days": 30,
                "active": True,
            },
        )
        start_trial(user)
        client = Client()
        client.login(username="trial", password="pass")
        response = client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
