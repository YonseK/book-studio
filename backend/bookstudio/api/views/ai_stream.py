"""SSE 스트리밍 엔드포인트."""

import json
import logging
import time

from django.http import StreamingHttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from bookstudio.models.ai import AISession
from bookstudio import conf

logger = logging.getLogger(__name__)

TERMINAL_STATUSES = {"COMPLETE", "FAILED", "CANCELLED"}


def _sse_format(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def ai_session_stream(request, session_id):
    """
    SSE 스트리밍: Celery → Redis → 이 뷰 → 클라이언트.
    Redis 없으면 polling fallback.
    """
    try:
        session = AISession.objects.get(pk=session_id, user=request.user)
    except AISession.DoesNotExist:
        return StreamingHttpResponse(
            _sse_format("error", {"message": "Session not found"}),
            content_type="text/event-stream",
            status=404,
        )

    def event_stream():
        # 초기 상태
        yield _sse_format("session_status", {
            "session_id": session.id,
            "status": session.status,
            "plan": session.plan,
            "completed_pages": session.completed_pages,
            "total_pages": session.total_pages,
        })

        if session.status in TERMINAL_STATUSES:
            yield _sse_format("done", {"status": session.status})
            return

        # Redis pub/sub 시도
        try:
            from django.core.cache import caches

            cache = caches["default"]
            if hasattr(cache, "client"):
                yield from _redis_stream(cache, session_id)
                return
        except Exception:
            pass

        # Polling fallback
        yield from _polling_stream(session)

    response = StreamingHttpResponse(event_stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


def _redis_stream(cache, session_id):
    """Redis pub/sub 기반 스트리밍."""
    channel = f"{conf.AI_REDIS_CHANNEL_PREFIX}:{session_id}"
    pubsub = cache.client.get_client().pubsub()
    pubsub.subscribe(channel)
    try:
        for message in pubsub.listen():
            if message["type"] == "message":
                event_data = json.loads(message["data"])
                yield _sse_format(event_data["event"], event_data["data"])
                if event_data["event"] in ("generation_complete", "error"):
                    yield _sse_format("done", {})
                    return
    except GeneratorExit:
        logger.info(f"SSE client disconnected: {session_id}")
    finally:
        pubsub.unsubscribe(channel)
        pubsub.close()


def _polling_stream(session):
    """Redis 없을 때 DB polling fallback."""
    last_completed = session.completed_pages
    for _ in range(600):  # 최대 10분
        time.sleep(1)
        session.refresh_from_db()

        if session.completed_pages > last_completed:
            yield _sse_format("progress", {
                "completed_pages": session.completed_pages,
                "total_pages": session.total_pages,
            })
            last_completed = session.completed_pages

        if session.status in TERMINAL_STATUSES:
            yield _sse_format("done", {"status": session.status})
            return

    yield _sse_format("timeout", {})
