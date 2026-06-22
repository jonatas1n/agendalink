import json
import logging
from decimal import Decimal
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from django.conf import settings

logger = logging.getLogger(__name__)


class AsaasError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def _api_key() -> str:
    key = getattr(settings, "ASAAS_API_KEY", "") or ""
    if not key:
        raise AsaasError("Integração Asaas não configurada (ASAAS_API_KEY).")
    return key


def _base_url() -> str:
    return (
        getattr(settings, "ASAAS_BASE_URL", "") or "https://sandbox.asaas.com/api/v3"
    ).rstrip("/")


def _request(method: str, path: str, payload: dict | None = None) -> dict:
    url = f"{_base_url()}{path}"
    body = None
    headers = {
        "access_token": _api_key(),
        "Content-Type": "application/json",
        "User-Agent": "agendalink/1.0",
    }
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
    req = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            if not raw:
                return {}
            return json.loads(raw)
    except HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        logger.warning("Asaas HTTP %s: %s", e.code, detail[:500])
        message = "Não foi possível concluir a operação no Asaas."
        try:
            parsed = json.loads(detail)
            errors = parsed.get("errors") or []
            if errors and isinstance(errors, list):
                first = errors[0]
                if isinstance(first, dict) and first.get("description"):
                    message = first["description"]
        except (json.JSONDecodeError, TypeError, KeyError):
            pass
        raise AsaasError(message, status_code=e.code) from e
    except OSError as e:
        logger.exception("Asaas request failed")
        raise AsaasError("Falha de comunicação com o Asaas.") from e


def create_customer(*, name: str, email: str, cpf_cnpj: str) -> dict:
    return _request(
        "POST",
        "/customers",
        {
            "name": name,
            "email": email,
            "cpfCnpj": cpf_cnpj,
        },
    )


def create_subscription(
    *,
    customer_id: str,
    value: Decimal,
    cycle: str = "MONTHLY",
    billing_type: str = "UNDEFINED",
    next_due_date: str,
    description: str = "Assinatura agendalink",
) -> dict:
    return _request(
        "POST",
        "/subscriptions",
        {
            "customer": customer_id,
            "billingType": billing_type,
            "value": float(value),
            "cycle": cycle,
            "nextDueDate": next_due_date,
            "description": description,
        },
    )


def list_subscription_payments(subscription_id: str) -> list:
    data = _request("GET", f"/subscriptions/{subscription_id}/payments")
    return data.get("data") or []
