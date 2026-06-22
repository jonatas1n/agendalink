import re
import secrets

from django.core.exceptions import ValidationError
from django.utils.text import slugify

RESERVED_STORE_SLUGS = frozenset(
    {
        "admin",
        "api",
        "auth",
        "appointments",
        "dashboard",
        "loja",
        "lojas",
        "products",
        "static",
        "media",
        "login",
        "logout",
        "register",
        "cadastro",
        "espaco",
        "billing",
    }
)

SLUG_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{1,78}[a-z0-9])?$")


def normalize_store_slug(raw: str) -> str:
    value = slugify((raw or "").strip(), allow_unicode=False)
    return value.strip("-")


def validate_store_slug(raw: str, *, exclude_profile_id=None) -> str:
    slug = normalize_store_slug(raw)
    if len(slug) < 3:
        raise ValidationError(
            "Use pelo menos 3 caracteres (letras, números ou hífens)."
        )
    if len(slug) > 80:
        raise ValidationError("Endereço muito longo (máximo 80 caracteres).")
    if not SLUG_RE.match(slug):
        raise ValidationError("Use apenas letras minúsculas, números e hífens.")
    if slug in RESERVED_STORE_SLUGS:
        raise ValidationError("Este endereço não está disponível.")
    from core.models import StoreProfile

    qs = StoreProfile.objects.filter(slug=slug)
    if exclude_profile_id:
        qs = qs.exclude(pk=exclude_profile_id)
    if qs.exists():
        raise ValidationError("Este endereço já está em uso. Escolha outro.")
    return slug


def generate_store_public_id() -> str:
    """32 caracteres hexadecimais (128 bits), não sequencial."""
    return secrets.token_hex(16)


def unique_public_id():
    from core.models import StoreProfile

    for _ in range(32):
        candidate = generate_store_public_id()
        if not StoreProfile.objects.filter(public_id=candidate).exists():
            return candidate
    raise RuntimeError("Não foi possível gerar ID público único da loja.")
