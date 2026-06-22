from django.db import models
from django.contrib.auth.models import User

from core.currency import format_currency
from core.duration import format_duration_minutes


class Product(models.Model):
    PRICE_TYPE = [
        ("unico", "Preço único"),
        ("porcao", "Por opção"),
    ]
    PRICE_CRITERION = [
        ("duracao", "Por duração"),
        ("tipo", "Por tipo"),
        ("tamanho", "Por tamanho"),
        ("outros", "Outros"),
    ]

    SERVICE_KIND = [
        ("agendamento", "Agendamento"),
        ("outros", "Outros"),
    ]
    CONTACT_CHANNEL = [
        ("email", "E-mail"),
        ("whatsapp", "WhatsApp"),
        ("both", "E-mail e WhatsApp"),
    ]

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="products",
        db_column="proprietario_id",
    )
    space = models.ForeignKey(
        "espacos.Space",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        db_column="espaco_id",
    )
    name = models.CharField(max_length=200, db_column="nome")
    description = models.TextField(blank=True, db_column="descricao")
    image = models.ImageField(
        upload_to="produtos/", blank=True, null=True, db_column="imagem"
    )
    price_type = models.CharField(
        max_length=10,
        choices=PRICE_TYPE,
        default="unico",
        db_column="tipo_preco",
    )
    price_criterion = models.CharField(
        max_length=20,
        choices=PRICE_CRITERION,
        default="duracao",
        verbose_name="Critério de preço",
        db_column="criterio_preco",
    )
    price_criterion_label = models.CharField(
        max_length=80,
        blank=True,
        verbose_name="Nome do critério (Outros)",
        help_text="Ex.: Pacote, Modalidade — quando o critério é Outros.",
        db_column="criterio_preco_rotulo",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, db_column="preco")
    duration_minutes = models.PositiveIntegerField(
        default=60, db_column="duracao_minutos"
    )
    simultaneous_capacity = models.PositiveIntegerField(
        default=1, db_column="capacidade_simultanea"
    )
    service_kind = models.CharField(
        max_length=20,
        choices=SERVICE_KIND,
        default="agendamento",
        db_column="tipo_servico",
        verbose_name="Tipo de serviço",
    )
    contact_channel = models.CharField(
        max_length=20,
        choices=CONTACT_CHANNEL,
        blank=True,
        db_column="canal_contato",
        verbose_name="Canal de contato",
    )
    active = models.BooleanField(default=True, db_column="ativo")
    created_at = models.DateTimeField(auto_now_add=True, db_column="criado_em")
    updated_at = models.DateTimeField(auto_now=True, db_column="atualizado_em")

    class Meta:
        verbose_name = "Produto/Serviço"
        verbose_name_plural = "Produtos/Serviços"
        ordering = ["-created_at"]
        db_table = "produtos_produto"

    def __str__(self):
        return self.name

    def is_outros(self):
        return self.service_kind == "outros"

    def contact_uses_email(self):
        return self.contact_channel in ("email", "both")

    def contact_uses_whatsapp(self):
        return self.contact_channel in ("whatsapp", "both")

    def duration_display(self):
        return format_duration_minutes(self.duration_minutes)

    def sync_primary_price(self):
        """Align price, duration and price_type with registered options."""
        prices = list(self.prices.order_by("sort_order", "pk"))
        if not prices:
            return
        first = prices[0]
        price_type = "porcao" if len(prices) > 1 else "unico"
        update_fields = []
        if self.price != first.price:
            self.price = first.price
            update_fields.append("price")
        if self.price_criterion == "duracao" and first.duration_minutes is not None:
            if self.duration_minutes != first.duration_minutes:
                self.duration_minutes = first.duration_minutes
                update_fields.append("duration_minutes")
        if self.price_type != price_type:
            self.price_type = price_type
            update_fields.append("price_type")
        if update_fields:
            update_fields.append("updated_at")
            self.save(update_fields=update_fields)

    def format_price(self):
        return format_currency(self.price, symbol=True)

    def criterion_display_label(self):
        if self.price_criterion == "outros" and self.price_criterion_label.strip():
            return self.price_criterion_label.strip()
        return self.get_price_criterion_display()

    def prices_summary(self):
        if self.is_outros():
            if self.contact_channel:
                return f"Contato · {self.get_contact_channel_display()}"
            return "Contato"
        options = list(self.prices.order_by("sort_order", "pk"))
        if not options:
            return f"{self.format_price()} · {self.duration_display()}"
        if len(options) == 1:
            option = options[0]
            return f"{option.format_price()} · {option.variation_label()}"
        return " · ".join(
            f"{option.format_price()} ({option.variation_label()})"
            for option in options
        )


class ProductPrice(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="prices",
        db_column="produto_id",
    )
    duration_minutes = models.PositiveIntegerField(
        null=True, blank=True, db_column="duracao_minutos"
    )
    label = models.CharField(max_length=120, blank=True, db_column="rotulo")
    price = models.DecimalField(max_digits=10, decimal_places=2, db_column="preco")
    sort_order = models.PositiveSmallIntegerField(default=0, db_column="ordem")

    class Meta:
        verbose_name = "Opção de preço"
        verbose_name_plural = "Opções de preço"
        ordering = ["sort_order", "duration_minutes", "pk"]
        db_table = "produtos_produtopreco"
        constraints = [
            models.UniqueConstraint(
                fields=["product", "label"],
                name="produto_preco_rotulo_unico",
            ),
        ]

    def variation_label(self):
        if (
            self.product.price_criterion == "duracao"
            and self.duration_minutes is not None
        ):
            return format_duration_minutes(self.duration_minutes)
        return self.label

    def format_price(self):
        return format_currency(self.price, symbol=True)

    def __str__(self):
        return f"{self.product.name} — {self.variation_label()}: {self.format_price()}"


class WeeklyAvailability(models.Model):
    WEEKDAYS = [
        (0, "Segunda"),
        (1, "Terça"),
        (2, "Quarta"),
        (3, "Quinta"),
        (4, "Sexta"),
        (5, "Sábado"),
        (6, "Domingo"),
    ]
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="weekly_availabilities",
        db_column="produto_id",
    )
    weekday = models.IntegerField(choices=WEEKDAYS, db_column="dia_semana")
    start_time = models.TimeField(db_column="hora_inicio")
    end_time = models.TimeField(db_column="hora_fim")

    class Meta:
        unique_together = ["product", "weekday", "start_time"]
        ordering = ["weekday", "start_time"]
        db_table = "produtos_disponibilidadesemanal"

    def __str__(self):
        return (
            f"{self.product.name} — {self.get_weekday_display()} "
            f"{self.start_time:%H:%M}–{self.end_time:%H:%M}"
        )


class DateBlock(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="date_blocks",
        db_column="produto_id",
    )
    date = models.DateField(db_column="data")
    reason = models.CharField(max_length=200, blank=True, db_column="motivo")

    class Meta:
        unique_together = ["product", "date"]
        db_table = "produtos_bloqueiodata"

    def __str__(self):
        return f"{self.product.name} — bloqueio em {self.date:%d/%m/%Y}"


class UnavailablePeriod(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="unavailable_periods",
        db_column="produto_id",
    )
    start_date = models.DateField(db_column="data_inicio")
    end_date = models.DateField(db_column="data_fim")
    reason = models.CharField(max_length=200, blank=True, db_column="motivo")

    class Meta:
        ordering = ["start_date", "pk"]
        db_table = "produtos_periodoindisponivel"

    def __str__(self):
        if self.start_date == self.end_date:
            return f"{self.product.name} — indisponível em {self.start_date:%d/%m/%Y}"
        return (
            f"{self.product.name} — indisponível "
            f"{self.start_date:%d/%m/%Y}–{self.end_date:%d/%m/%Y}"
        )


class DateAvailability(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="date_availabilities",
        db_column="produto_id",
    )
    date = models.DateField(db_column="data")
    start_time = models.TimeField(db_column="hora_inicio")
    end_time = models.TimeField(db_column="hora_fim")

    class Meta:
        ordering = ["date", "start_time"]
        unique_together = ["product", "date", "start_time"]
        db_table = "produtos_disponibilidadedata"

    def __str__(self):
        return (
            f"{self.product.name} — {self.date:%d/%m/%Y} "
            f"{self.start_time:%H:%M}–{self.end_time:%H:%M}"
        )
