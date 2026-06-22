from django.conf import settings
from django.db import models


class BillingPlan(models.Model):
    slug = models.SlugField(unique=True, max_length=40)
    name = models.CharField("Nome", max_length=120)
    price = models.DecimalField(
        "Preço mensal", max_digits=10, decimal_places=2, default=0
    )
    trial_days = models.PositiveSmallIntegerField("Dias de trial", default=0)
    asaas_cycle = models.CharField(
        "Ciclo Asaas",
        max_length=20,
        blank=True,
        help_text="Ex.: MONTHLY para planos pagos.",
    )
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "plano de assinatura"
        verbose_name_plural = "planos de assinatura"

    def __str__(self):
        return self.name


class StoreSubscription(models.Model):
    STATUS_PENDING = "pending"
    STATUS_TRIALING = "trialing"
    STATUS_ACTIVE = "active"
    STATUS_PAST_DUE = "past_due"
    STATUS_CANCELED = "canceled"
    STATUS_BLOCKED = "blocked"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pendente"),
        (STATUS_TRIALING, "Trial"),
        (STATUS_ACTIVE, "Ativo"),
        (STATUS_PAST_DUE, "Inadimplente"),
        (STATUS_CANCELED, "Cancelado"),
        (STATUS_BLOCKED, "Bloqueado"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="store_subscription",
    )
    plan = models.ForeignKey(
        BillingPlan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    delinquency_since = models.DateTimeField(null=True, blank=True)
    trial_used = models.BooleanField(default=False)
    cpf_cnpj = models.CharField("CPF/CNPJ", max_length=14, blank=True)
    asaas_customer_id = models.CharField(max_length=64, blank=True)
    asaas_subscription_id = models.CharField(max_length=64, blank=True)
    pending_invoice_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "assinatura da loja"
        verbose_name_plural = "assinaturas da loja"

    def __str__(self):
        return f"Assinatura de {self.user_id} ({self.status})"


class AsaasWebhookEvent(models.Model):
    event_key = models.CharField(max_length=128, unique=True)
    event_type = models.CharField(max_length=80, blank=True)
    processed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "evento webhook Asaas"
        verbose_name_plural = "eventos webhook Asaas"

    def __str__(self):
        return self.event_key
