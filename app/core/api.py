from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from core.store_profile import get_store_profile
from core.store_slug import validate_store_slug


@login_required
@require_GET
def check_store_slug(request):
    raw = request.GET.get("slug", "")
    profile = get_store_profile(request.user)
    try:
        slug = validate_store_slug(raw, exclude_profile_id=profile.pk)
    except ValidationError as e:
        message = e.messages[0] if e.messages else str(e)
        return JsonResponse({"ok": False, "erro": message}, status=400)
    return JsonResponse({"ok": True, "slug": slug})
