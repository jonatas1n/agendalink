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
            name="StoreProfile",
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
                    "name",
                    models.CharField(
                        blank=True, max_length=120, verbose_name="Nome da loja"
                    ),
                ),
                (
                    "tagline",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="Frase de destaque"
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="Sobre a loja"),
                ),
                (
                    "public_email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="E-mail público"
                    ),
                ),
                (
                    "public_phone",
                    models.CharField(
                        blank=True, max_length=20, verbose_name="Telefone / WhatsApp"
                    ),
                ),
                (
                    "city",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="Cidade ou região"
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="store_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "perfil da loja",
                "verbose_name_plural": "perfis da loja",
            },
        ),
    ]
