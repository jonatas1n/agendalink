from decimal import Decimal

from django.db import migrations


def seed_plans(apps, schema_editor):
    BillingPlan = apps.get_model("billing", "BillingPlan")
    plans = [
        {
            "slug": "trial_30",
            "name": "Trial 30 dias",
            "price": Decimal("0.00"),
            "trial_days": 30,
            "asaas_cycle": "",
            "active": True,
        },
        {
            "slug": "paid_monthly",
            "name": "Plano mensal",
            "price": Decimal("49.90"),
            "trial_days": 0,
            "asaas_cycle": "MONTHLY",
            "active": True,
        },
    ]
    for data in plans:
        BillingPlan.objects.update_or_create(slug=data["slug"], defaults=data)


def unseed_plans(apps, schema_editor):
    BillingPlan = apps.get_model("billing", "BillingPlan")
    BillingPlan.objects.filter(slug__in=["trial_30", "paid_monthly"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("billing", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_plans, unseed_plans),
    ]
