"""Celery 태스크: AI 기획서 생성 + 콘텐츠 생성."""

import json
import logging

from bookstudio.models.ai import AISession, AISessionStatusEnum

logger = logging.getLogger(__name__)


def _make_redis_emitter(session_id: str):
    """Celery 워커 → Redis pub/sub 이벤트 발행 콜백."""
    from bookstudio import conf

    def emit(event_type: str, data: dict):
        try:
            from django.core.serializers.json import DjangoJSONEncoder

            channel = f"{conf.AI_REDIS_CHANNEL_PREFIX}:{session_id}"
            message = json.dumps(
                {"event": event_type, "data": data}, cls=DjangoJSONEncoder,
            )

            # Channels layer 사용
            try:
                from channels.layers import get_channel_layer
                from asgiref.sync import async_to_sync

                layer = get_channel_layer()
                if layer:
                    async_to_sync(layer.group_send)(
                        f"ai_session_{session_id}",
                        {"type": "ai.event", "event": event_type, "data": data},
                    )
                    return
            except ImportError:
                pass

            # Redis 직접 publish fallback
            try:
                from django.core.cache import caches

                cache = caches["default"]
                if hasattr(cache, "client"):
                    cache.client.get_client().publish(channel, message)
            except Exception:
                pass

        except Exception as e:
            logger.warning(f"Failed to emit event {event_type}: {e}")

    return emit


try:
    from celery import shared_task

    @shared_task(bind=True, max_retries=0, ignore_result=False)
    def run_ai_planning(self, session_id: str) -> dict:
        """기획서 생성 태스크."""
        from bookstudio.services.ai.orchestrator import OrchestratorService

        session = AISession.objects.select_related("book", "edition").get(
            pk=session_id,
        )
        session.celery_task_id = self.request.id or ""
        session.save(update_fields=["celery_task_id"])

        try:
            emitter = _make_redis_emitter(session_id)
            orchestrator = OrchestratorService(event_callback=emitter)
            plan = orchestrator.run_planning(session)
            return {"status": "ok", "plan": plan}
        except Exception as exc:
            session.mark_failed(str(exc))
            raise

    @shared_task(bind=True, max_retries=1, default_retry_delay=5)
    def run_ai_generation(self, session_id: str) -> dict:
        """콘텐츠 + 디자인 생성 태스크."""
        from bookstudio.services.ai.orchestrator import OrchestratorService

        session = AISession.objects.select_related(
            "book", "edition", "pattern_set",
        ).get(pk=session_id)

        if session.status != AISessionStatusEnum.APPROVED:
            return {"status": "skipped", "reason": f"status is {session.status}"}

        session.celery_task_id = self.request.id or ""
        session.save(update_fields=["celery_task_id"])

        try:
            emitter = _make_redis_emitter(session_id)
            orchestrator = OrchestratorService(event_callback=emitter)
            orchestrator.run_generation(session)
            session.refresh_from_db()
            return {"status": "ok", "completed_pages": session.completed_pages}
        except Exception as exc:
            session.mark_failed(str(exc))
            raise self.retry(exc=exc)

except ImportError:
    # Celery가 설치되지 않은 환경 — 동기 fallback만 사용
    pass
