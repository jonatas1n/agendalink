import json
import re

from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def normalize_phone(value: str) -> str:
    return re.sub(r"\D", "", (value or "").strip())


def parse_client_payload(data: dict):
    raw = data.get("client") or {}
    if not raw:
        return None

    if isinstance(raw, str):
        return None

    name = (raw.get("name") or "").strip()
    cpf = raw.get("cpf") or ""
    email = (raw.get("email") or "").strip()
    phone = raw.get("phone") or ""
    confirm_email = raw.get("confirm_via_email", False)
    confirm_phone = raw.get("confirm_via_phone", False)

    if isinstance(confirm_email, str):
        confirm_email = confirm_email.lower() in ("1", "true", "sim", "yes")
    if isinstance(confirm_phone, str):
        confirm_phone = confirm_phone.lower() in ("1", "true", "sim", "yes")

    return {
        "name": name,
        "cpf": cpf,
        "email": email,
        "phone": phone,
        "confirm_via_email": bool(confirm_email),
        "confirm_via_phone": bool(confirm_phone),
    }


def validate_client_for_booking(client: dict):
    from core.cpf import is_valid_cpf, normalize_cpf

    if not client:
        raise ValidationError("Informe os dados do cliente.")

    name = client.get("name", "").strip()
    if len(name) < 2:
        raise ValidationError("Informe seu nome completo.")

    cpf = normalize_cpf(client.get("cpf", ""))
    if not is_valid_cpf(cpf):
        raise ValidationError("CPF inválido.")

    email = client.get("email", "").strip()
    if not email:
        raise ValidationError("Informe um e-mail.")
    try:
        validate_email(email)
    except ValidationError:
        raise ValidationError("Informe um e-mail válido.")

    confirm_phone = client.get("confirm_via_phone", False)

    phone = normalize_phone(client.get("phone", ""))
    if confirm_phone and len(phone) < 10:
        raise ValidationError(
            "Informe um telefone válido com DDD para confirmação por WhatsApp."
        )

    client["cpf"] = cpf
    client["name"] = name
    client["email"] = email
    client["phone"] = phone
    client["confirm_via_email"] = True
    return client
