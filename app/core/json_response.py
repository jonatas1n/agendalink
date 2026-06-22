from django.http import JsonResponse


def json_error(message: str, status: int = 400) -> JsonResponse:
    return JsonResponse({"erro": message}, status=status)
