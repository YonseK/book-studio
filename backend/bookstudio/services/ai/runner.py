"""AI 생성 실행기. Celery 유무에 따라 분기."""

from bookstudio import conf
from bookstudio.models.ai import AISession


def start_planning(session: AISession):
    """기획서 생성 시작."""
    if conf.AI_USE_CELERY:
        from bookstudio.tasks import run_ai_planning
        run_ai_planning.delay(session.id)
    else:
        from bookstudio.services.ai.orchestrator import OrchestratorService
        orchestrator = OrchestratorService()
        orchestrator.run_planning(session)


def start_generation(session: AISession):
    """콘텐츠 생성 시작."""
    if conf.AI_USE_CELERY:
        from bookstudio.tasks import run_ai_generation
        run_ai_generation.delay(session.id)
    else:
        from bookstudio.services.ai.orchestrator import OrchestratorService
        orchestrator = OrchestratorService()
        orchestrator.run_generation(session)
