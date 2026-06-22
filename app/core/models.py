from django.conf import settings
from django.db import models
from django.urls import reverse

from core.store_slug import unique_public_id


class StoreProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="store_profile",
    )
    public_id = models.CharField(
        "ID público da loja",
        max_length=32,
        unique=True,
        blank=True,
        db_index=True,
    )
    slug = models.SlugField(
        "Endereço da loja",
        max_length=80,
        unique=True,
        blank=True,
        help_text="Parte da URL pública: /loja/seu-endereco/",
    )
    name = models.CharField("Nome da loja", max_length=120, blank=True)
    tagline = models.CharField("Frase de destaque", max_length=200, blank=True)
    description = models.TextField("Sobre a loja", blank=True)
    public_email = models.EmailField("E-mail público", blank=True)
    public_phone = models.CharField("Telefone / WhatsApp", max_length=20, blank=True)
    city = models.CharField("Cidade ou região", max_length=100, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "perfil da loja"
        verbose_name_plural = "perfis da loja"

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        name = (self.name or "").strip()
        if name:
            return name
        user = self.user
        full = user.get_full_name().strip() if user else ""
        if full:
            return full
        return user.username if user else ""

    def save(self, *args, **kwargs):
        if not self.public_id:
            self.public_id = unique_public_id()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        if self.slug:
            return reverse("public_store", args=[self.slug])
        return ""
