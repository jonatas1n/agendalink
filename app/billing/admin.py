from django.contrib import admin

from .models import AsaasWebhookEvent, BillingPlan, StoreSubscription


@admin.register(BillingPlan)
class BillingPlanAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "price", "trial_days", "active")
    list_filter = ("active",)


@admin.register(StoreSubscription)
class StoreSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "status",
        "plan",
        "trial_ends_at",
        "delinquency_since",
        "asaas_customer_id",
        "asaas_subscription_id",
    )
    list_filter = ("status",)
    search_fields = (
        "user__username",
        "user__email",
        "asaas_customer_id",
        "asaas_subscription_id",
    )
    raw_id_fields = ("user",)


@admin.register(AsaasWebhookEvent)
class AsaasWebhookEventAdmin(admin.ModelAdmin):
    list_display = ("event_key", "event_type", "processed_at")
    search_fields = ("event_key", "event_type")
