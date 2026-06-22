from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Space(models.Model):
    admin = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="spaces_admin"
    )
    name = models.CharField(max_length=200, db_column="nome")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True, db_column="descricao")
    address = models.CharField(max_length=300, blank=True, db_column="endereco")
    logo = models.ImageField(upload_to="espacos/logos/", blank=True, null=True)
    cover_photo = models.ImageField(
        upload_to="espacos/capas/",
        blank=True,
        null=True,
        db_column="foto_capa",
    )
    collective_schedule_active = models.BooleanField(
        default=False,
        db_column="agenda_coletiva_ativa",
        help_text="Se ativo, os membros do espaço podem ver os agendamentos de todos os outros membros.",
    )
    active = models.BooleanField(default=True, db_column="ativo")
    created_at = models.DateTimeField(auto_now_add=True, db_column="criado_em")

    class Meta:
        verbose_name = "Espaço"
        verbose_name_plural = "Espaços"
        ordering = ["name"]
        db_table = "espacos_espaco"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            n = 1
            while Space.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("public_space", args=[self.slug])


class SpaceMember(models.Model):
    ROLE_CHOICES = [
        ("membro", "Membro"),
        ("admin", "Administrador"),
    ]
    STATUS_CHOICES = [
        ("ativo", "Ativo"),
        ("pendente", "Pendente"),
        ("inativo", "Inativo"),
    ]

    space = models.ForeignKey(
        Space,
        on_delete=models.CASCADE,
        related_name="members",
        db_column="espaco_id",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="space_memberships",
        db_column="usuario_id",
    )
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default="membro", db_column="papel"
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="ativo")
    bio = models.TextField(
        blank=True, help_text="Apresentação pública do profissional neste espaço."
    )
    profile_photo = models.ImageField(
        upload_to="membros/",
        blank=True,
        null=True,
        db_column="foto_perfil",
    )
    specialty = models.CharField(max_length=150, blank=True, db_column="especialidade")
    joined_at = models.DateTimeField(auto_now_add=True, db_column="entrou_em")

    class Meta:
        verbose_name = "Membro do Espaço"
        verbose_name_plural = "Membros do Espaço"
        unique_together = ["space", "user"]
        db_table = "espacos_membroespaco"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} @ {self.space.name}"

    def is_admin(self):
        return self.role == "admin" or self.user == self.space.admin
