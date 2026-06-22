import json
import logging

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from billing.services.subscription import apply_asaas_webhook

logger = logging.getLogger(__name__)


def _webhook_token_ok(request) -> bool:
    expected = getattr(settings, "ASAAS_WEBHOOK_ACCESS_TOKEN", "") or ""
    if not expected:
        return settings.DEBUG
    token = (
        request.headers.get("asaas-access-token")
        or request.GET.get("access_token")
        or ""
    )
    return token == expected


@csrf_exempt
@require_POST
def asaas_webhook(request):
    if not _webhook_token_ok(request):
        return HttpResponseForbidden("Token inválido.")
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"erro": "JSON inválido."}, status=400)

    try:
        apply_asaas_webhook(payload)
    except Exception:
        logger.exception("Falha ao processar webhook Asaas")
        return JsonResponse({"erro": "Erro interno."}, status=500)

    return JsonResponse({"ok": True})
