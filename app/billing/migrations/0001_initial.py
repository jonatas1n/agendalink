# Generated manually for billing app

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BillingPlan",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("slug", models.SlugField(max_length=40, unique=True)),
                ("name", models.CharField(max_length=120, verbose_name="Nome")),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=10,
                        verbose_name="Preço mensal",
                    ),
                ),
                (
                    "trial_days",
                    models.PositiveSmallIntegerField(
                        default=0, verbose_name="Dias de trial"
                    ),
                ),
                (
                    "asaas_cycle",
                    models.CharField(
                        blank=True,
                        help_text="Ex.: MONTHLY para planos pagos.",
                        max_length=20,
                        verbose_name="Ciclo Asaas",
                    ),
                ),
                ("active", models.BooleanField(default=True)),
            ],
            options={
                "verbose_name": "plano de assinatura",
                "verbose_name_plural": "planos de assinatura",
            },
        ),
        migrations.CreateModel(
            name="AsaasWebhookEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("event_key", models.CharField(max_length=128, unique=True)),
                ("event_type", models.CharField(blank=True, max_length=80)),
                ("processed_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "evento webhook Asaas",
                "verbose_name_plural": "eventos webhook Asaas",
            },
        ),
        migrations.CreateModel(
            name="StoreSubscription",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pendente"),
                            ("trialing", "Trial"),
                            ("active", "Ativo"),
                            ("past_due", "Inadimplente"),
                            ("canceled", "Cancelado"),
                            ("blocked", "Bloqueado"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("trial_ends_at", models.DateTimeField(blank=True, null=True)),
                ("current_period_end", models.DateTimeField(blank=True, null=True)),
                ("delinquency_since", models.DateTimeField(blank=True, null=True)),
                ("trial_used", models.BooleanField(default=False)),
                (
                    "cpf_cnpj",
                    models.CharField(
                        blank=True, max_length=14, verbose_name="CPF/CNPJ"
                    ),
                ),
                ("asaas_customer_id", models.CharField(blank=True, max_length=64)),
                ("asaas_subscription_id", models.CharField(blank=True, max_length=64)),
                ("pending_invoice_url", models.URLField(blank=True, max_length=500)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "plan",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="subscriptions",
                        to="billing.billingplan",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="store_subscription",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "assinatura da loja",
                "verbose_name_plural": "assinaturas da loja",
            },
        ),
    ]
