import secrets

from django.db import migrations, models
from django.utils.text import slugify


def _backfill_slugs(apps, schema_editor):
    StoreProfile = apps.get_model("core", "StoreProfile")
    User = apps.get_model("auth", "User")
    used = set(StoreProfile.objects.exclude(slug="").values_list("slug", flat=True))

    for profile in StoreProfile.objects.all():
        if not profile.public_id:
            profile.public_id = secrets.token_hex(16)
        if not profile.slug:
            user = User.objects.filter(pk=profile.user_id).first()
            base = (
                slugify(user.username if user else f"loja-{profile.pk}")
                or f"loja-{profile.pk}"
            )
            slug = base
            n = 1
            while slug in used:
                slug = f"{base}-{n}"
                n += 1
            used.add(slug)
            profile.slug = slug
        profile.save(update_fields=["slug", "public_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_storeprofile"),
    ]

    operations = [
        migrations.AddField(
            model_name="storeprofile",
            name="public_id",
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=32,
                unique=True,
                verbose_name="ID público da loja",
            ),
        ),
        migrations.AddField(
            model_name="storeprofile",
            name="slug",
            field=models.SlugField(
                blank=True,
                max_length=80,
                unique=True,
                verbose_name="Endereço da loja",
            ),
        ),
        migrations.RunPython(_backfill_slugs, migrations.RunPython.noop),
    ]
