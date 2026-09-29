import json
import logging

from django.conf import settings
from django.http import JsonResponse
from django.utils.module_loading import import_string
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

logger = logging.getLogger(__name__)
MAX_MESSAGE_LENGTH = 2000
MAX_AUDIO_BYTES = 10 * 1024 * 1024


def _authenticated(request):
    return request.user.is_authenticated


def _run_command(user, message):
    handler_path = getattr(settings, "LIZA_COMMAND_HANDLER", "")
    if not handler_path:
        return None, JsonResponse({"error": "Liza Django handler'i sozlanmagan."}, status=503)

    try:
        handler = import_string(handler_path)
        result = handler(user=user, message=message)
    except Exception:
        logger.exception("Liza command handler failed")
        return None, JsonResponse({"error": "Buyruqni bajarishda xatolik yuz berdi."}, status=500)

    reply = result.get("reply", "") if isinstance(result, dict) else result
    if not isinstance(reply, str):
        return None, JsonResponse({"error": "Handler matnli javob qaytarishi kerak."}, status=500)
    return reply, None


@require_GET
@ensure_csrf_cookie
def csrf_token(request):
    if not _authenticated(request):
        return JsonResponse({"error": "Kirish talab qilinadi."}, status=401)
    return JsonResponse({"csrfToken": get_token(request)})


@require_POST
@csrf_protect
@ensure_csrf_cookie
def command(request):
    if not _authenticated(request):
        return JsonResponse({"error": "Kirish talab qilinadi."}, status=401)

    try:
        if int(request.META.get("CONTENT_LENGTH") or 0) > 16_384:
            return JsonResponse({"error": "So'rov hajmi juda katta."}, status=413)
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
        return JsonResponse({"error": "JSON so'rovi noto'g'ri."}, status=400)

    if not isinstance(payload, dict):
        return JsonResponse({"error": "JSON obyekt yuborilishi kerak."}, status=400)

    message = payload.get("message")
    if not isinstance(message, str) or not message.strip():
        return JsonResponse({"error": "Xabar bo'sh bo'lmasligi kerak."}, status=400)
    message = message.strip()
    if len(message) > MAX_MESSAGE_LENGTH:
        return JsonResponse({"error": "Xabar juda uzun."}, status=413)

    reply, error = _run_command(request.user, message)
    if error:
        return error
    return JsonResponse({"reply": reply})


@require_POST
@csrf_protect
def voice(request):
    if not _authenticated(request):
        return JsonResponse({"error": "Kirish talab qilinadi."}, status=401)

    audio_file = request.FILES.get("audio")
    if audio_file is None:
        return JsonResponse({"error": "Ovoz fayli yuborilmadi."}, status=400)
    if audio_file.size > MAX_AUDIO_BYTES:
        return JsonResponse({"error": "Ovoz yozuvi 10 MB dan oshmasligi kerak."}, status=413)
    if audio_file.content_type.split(";")[0] not in {
        "audio/webm", "audio/mp4", "audio/ogg", "audio/wav", "audio/x-wav"
    }:
        return JsonResponse({"error": "Ovoz formati qo'llab-quvvatlanmaydi."}, status=415)

    transcriber_path = getattr(settings, "LIZA_TRANSCRIBE_HANDLER", "")
    if not transcriber_path:
        return JsonResponse({"error": "Liza transkripsiya handler'i sozlanmagan."}, status=503)
    try:
        transcriber = import_string(transcriber_path)
        transcript = transcriber(user=request.user, audio_file=audio_file)
    except Exception:
        logger.exception("Liza transcription handler failed")
        return JsonResponse({"error": "Ovozni matnga aylantirib bo'lmadi."}, status=500)

    if not isinstance(transcript, str) or not transcript.strip():
        return JsonResponse({"error": "Ovozdan matn aniqlanmadi."}, status=422)
    transcript = transcript.strip()
    if len(transcript) > MAX_MESSAGE_LENGTH:
        return JsonResponse({"error": "Aniqlangan matn juda uzun."}, status=413)

    reply, error = _run_command(request.user, transcript)
    if error:
        return error
    return JsonResponse({"transcript": transcript, "reply": reply})
