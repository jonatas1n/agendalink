from django.db import models
from django.contrib.auth.models import User

from produtos.models import Product


class Appointment(models.Model):
    STATUS_CHOICES = [
        ("pendente", "Pendente"),
        ("confirmado", "Confirmado"),
        ("cancelado", "Cancelado"),
        ("concluido", "Concluído"),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="appointments",
        db_column="produto_id",
    )
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="appointments",
        null=True,
        blank=True,
        db_column="cliente_id",
    )
    starts_at = models.DateTimeField(db_column="data_hora_inicio")
    ends_at = models.DateTimeField(db_column="data_hora_fim")
    status = models.CharField(
        max_length=15, choices=STATUS_CHOICES, default="confirmado"
    )
    notes = models.TextField(blank=True, db_column="observacoes")

    guest_name = models.CharField(max_length=200, blank=True)
    guest_cpf = models.CharField(max_length=11, blank=True)
    guest_email = models.EmailField(blank=True)
    guest_phone = models.CharField(max_length=32, blank=True)
    confirm_via_email = models.BooleanField(default=True)
    confirm_via_phone = models.BooleanField(default=False)

    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        db_column="valor_pago",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_column="criado_em")
    updated_at = models.DateTimeField(auto_now=True, db_column="atualizado_em")
    reminder_24h_sent = models.BooleanField(
        default=False, db_column="lembrete_24h_enviado"
    )
    reminder_1h_sent = models.BooleanField(
        default=False, db_column="lembrete_1h_enviado"
    )

    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
        ordering = ["-starts_at"]
        db_table = "agendamentos_agendamento"

    def display_customer_name(self):
        if self.guest_name:
            return self.guest_name
        if self.customer_id:
            return self.customer.get_full_name() or self.customer.username
        return "Cliente"

    def display_guest_cpf(self):
        from core.cpf import format_cpf_display

        if self.guest_cpf:
            return format_cpf_display(self.guest_cpf)
        return "—"

    def display_guest_email(self):
        if self.guest_email:
            return self.guest_email
        if self.customer_id and self.customer.email:
            return self.customer.email
        return "—"

    def display_guest_phone(self):
        if not self.guest_phone:
            return "—"
        digits = self.guest_phone
        if len(digits) == 11:
            return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
        if len(digits) == 10:
            return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"
        return self.guest_phone

    def recipient_email(self):
        if self.guest_email:
            return self.guest_email
        if self.customer_id and self.customer.email:
            return self.customer.email
        return ""

    def __str__(self):
        return (
            f"{self.display_customer_name()} - {self.product.name} - "
            f'{self.starts_at.strftime("%d/%m/%Y %H:%M")}'
        )

    def save(self, *args, **kwargs):
        if not self.amount_paid:
            self.amount_paid = self.product.price
        super().save(*args, **kwargs)
