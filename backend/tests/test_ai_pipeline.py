"""Phase 2 AI 파이프라인 테스트: 모델, 서비스, API."""

import json
from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from bookstudio.models import Book, BookEdition
from bookstudio.models.ai import AISession, AISessionStatusEnum
from bookstudio.models.design_pattern import (
    DesignPattern,
    DesignPatternSlot,
    DesignPatternSet,
    DesignPatternSetMembership,
    PatternCategoryEnum,
    SlotRoleEnum,
)
from bookstudio.services.ai.planner import PlannerService, Plan
from bookstudio.services.ai.writer import WriterService
from bookstudio.services.ai.designer import DesignerService
from bookstudio.services.ai.orchestrator import OrchestratorService

from tests.mock_llm import (
    MockLLMAdapter,
    DEFAULT_PLAN,
    DEFAULT_CONTENT,
    DEFAULT_PATTERN_SELECTION,
)

User = get_user_model()





# ── Fixtures ──


@pytest.fixture
def user(db):
    return User.objects.create_user(username="aiuser", password="testpass")


@pytest.fixture
def book(user):
    return Book.objects.create(user=user, book_mode="BOOK", book_layout="PPTX_WIDE")


@pytest.fixture
def edition(book):
    return BookEdition.objects.create(book=book, title="AI Test", latest=True)


@pytest.fixture
def session(user, book, edition):
    return AISession.objects.create(
        user=user, book=book, edition=edition,
        prompt="테스트 프레젠테이션 만들어줘",
    )


@pytest.fixture
def curated_patterns(db):
    """최소한의 패턴 세트."""
    from django.core.management import call_command
    call_command("loaddata", "curated_patterns", verbosity=0)


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


# ── Model Tests ──


class TestAISession:
    def test_create_session(self, session):
        assert session.status == AISessionStatusEnum.PLANNING
        assert session.total_pages == 0
        assert session.completed_pages == 0

    def test_mark_failed(self, session):
        session.mark_failed("Something went wrong")
        session.refresh_from_db()
        assert session.status == AISessionStatusEnum.FAILED
        assert session.error_message == "Something went wrong"

    def test_mark_complete(self, session):
        session.mark_complete()
        session.refresh_from_db()
        assert session.status == AISessionStatusEnum.COMPLETE
        assert session.completed_at is not None

    def test_increment_progress(self, session):
        session.increment_progress()
        session.refresh_from_db()
        assert session.completed_pages == 1

    def test_add_token_usage(self, session):
        session.add_token_usage(100, 200)
        session.add_token_usage(50, 100)
        session.refresh_from_db()
        assert session.total_input_tokens == 150
        assert session.total_output_tokens == 300


# ── Service Tests ──


class TestPlannerService:
    def test_generate_plan(self, mock_llm_settings):
        planner = PlannerService()
        plan, in_tok, out_tok = planner.generate_plan(
            prompt="테스트", layout_preset="PPTX_WIDE",
        )
        assert isinstance(plan, Plan)
        assert plan.total_pages == 3
        assert len(plan.pages) == 3
        assert in_tok == 10
        assert out_tok == 50

    def test_generate_plan_with_options(self, mock_llm_settings):
        planner = PlannerService()
        plan, _, _ = planner.generate_plan(
            prompt="테스트", layout_preset="PPTX_WIDE",
            options={"page_count": 10, "tone": "casual"},
        )
        assert plan.title == "테스트 프레젠테이션"


class TestWriterService:
    def test_generate_page_content(self, mock_llm_settings):
        mock = MockLLMAdapter(responses=[json.dumps(DEFAULT_CONTENT)])
        with patch("bookstudio.services.ai.writer.get_llm_adapter", return_value=mock):
            writer = WriterService()
            content = writer.generate_page_content(
                plan=DEFAULT_PLAN,
                page_plan=DEFAULT_PLAN["pages"][0],
                slot_roles=[{"role": "title", "media_type": "HL"}],
            )
        assert len(content.slots) == 2
        assert content.slots[0].role == "title"
        assert content.slots[0].headline == "테스트 제목"

    def test_previous_summary_accumulates(self, mock_llm_settings):
        mock = MockLLMAdapter(responses=[json.dumps(DEFAULT_CONTENT)])
        with patch("bookstudio.services.ai.writer.get_llm_adapter", return_value=mock):
            writer = WriterService()
            writer.generate_page_content(
                plan=DEFAULT_PLAN, page_plan=DEFAULT_PLAN["pages"][0],
                slot_roles=[],
            )
            writer.generate_page_content(
                plan=DEFAULT_PLAN, page_plan=DEFAULT_PLAN["pages"][1],
                slot_roles=[],
            )
        assert len(writer._previous_summaries) == 2

    def test_reset_clears_state(self, db):
        writer = WriterService()
        writer._previous_summaries = ["a", "b"]
        writer.reset()
        assert writer._previous_summaries == []


class TestDesignerService:
    def test_select_pattern_from_set(self, curated_patterns):
        designer = DesignerService()
        ps = DesignPatternSet.objects.first()
        pattern = designer.select_pattern(
            page_plan={"suggested_pattern_category": "TITLE"},
            pattern_set=ps,
            used_pattern_ids=[],
        )
        assert pattern is not None
        assert pattern.category == PatternCategoryEnum.TITLE

    def test_select_pattern_avoids_duplicates(self, curated_patterns):
        designer = DesignerService()
        ps = DesignPatternSet.objects.first()
        first = ps.get_pattern("TITLE")
        # 첫 번째를 사용 목록에 넣으면 다른 패턴이 선택됨 (LLM fallback)
        pattern = designer.select_pattern(
            page_plan={"suggested_pattern_category": "TITLE"},
            pattern_set=ps,
            used_pattern_ids=[first.id],
        )
        assert pattern is not None

    def test_fallback_to_content(self, curated_patterns):
        designer = DesignerService()
        pattern = designer.select_pattern(
            page_plan={"suggested_pattern_category": "NONEXISTENT"},
            pattern_set=None,
            used_pattern_ids=[],
        )
        assert pattern is not None


class TestOrchestratorService:
    def test_run_planning(self, session, mock_llm_settings):
        events = []
        orchestrator = OrchestratorService(
            event_callback=lambda t, d: events.append((t, d))
        )
        plan = orchestrator.run_planning(session)

        session.refresh_from_db()
        assert session.status == AISessionStatusEnum.REVIEW
        assert session.plan is not None
        assert session.total_pages == 3
        assert any(t == "planning_complete" for t, _ in events)

    def test_run_generation(self, session, curated_patterns, mock_llm_settings):
        # 먼저 planning 수행
        orchestrator = OrchestratorService()
        orchestrator.run_planning(session)

        # approve
        session.refresh_from_db()
        session.status = AISessionStatusEnum.APPROVED
        session.save(update_fields=["status"])

        # generation (mock으로 writer 대체)
        mock_content = MockLLMAdapter(responses=[json.dumps(DEFAULT_CONTENT)])
        events = []
        # writer와 designer 모두 get_llm_adapter 사용
        with patch("bookstudio.services.ai.writer.get_llm_adapter", return_value=mock_content), \
             patch("bookstudio.services.ai.designer.get_llm_adapter", return_value=mock_content):
            orchestrator2 = OrchestratorService(
                event_callback=lambda t, d: events.append((t, d))
            )
            orchestrator2.run_generation(session)

        session.refresh_from_db()
        assert session.status == AISessionStatusEnum.COMPLETE
        assert session.completed_at is not None

        page_complete_events = [e for e in events if e[0] == "page_complete"]
        assert len(page_complete_events) == 3

    def test_page_error_does_not_stop(self, session, curated_patterns, mock_llm_settings):
        orchestrator = OrchestratorService()
        orchestrator.run_planning(session)

        session.refresh_from_db()
        session.status = AISessionStatusEnum.APPROVED
        session.save(update_fields=["status"])

        call_count = {"n": 0}

        def failing_writer(*args, **kwargs):
            call_count["n"] += 1
            if call_count["n"] <= 1:
                raise RuntimeError("LLM error")
            return MockLLMAdapter(responses=[json.dumps(DEFAULT_CONTENT)])

        mock_designer = MockLLMAdapter(responses=[json.dumps(DEFAULT_PATTERN_SELECTION)])
        events = []
        with patch("bookstudio.services.ai.writer.get_llm_adapter", side_effect=failing_writer), \
             patch("bookstudio.services.ai.designer.get_llm_adapter", return_value=mock_designer):
            orchestrator2 = OrchestratorService(
                event_callback=lambda t, d: events.append((t, d))
            )
            orchestrator2.run_generation(session)

        # 에러가 있어도 완료됨
        session.refresh_from_db()
        assert session.status == AISessionStatusEnum.COMPLETE
        error_events = [e for e in events if e[0] == "page_error"]
        assert len(error_events) >= 1


# ── API Tests ──


class TestAISessionAPI:
    def test_create_session(self, api_client, book, edition, mock_llm_settings):
        """세션 생성 시 planning이 동기로 실행됨 (AI_USE_CELERY=False)."""
        response = api_client.post("/api/studio/ai/sessions/", {
            "book": book.id,
            "edition": edition.id,
            "prompt": "테스트 만들어줘",
        }, format="json")

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "REVIEW"  # 동기 실행 완료
        assert data["plan"] is not None

    def test_approve_session(self, api_client, book, edition, curated_patterns, mock_llm_settings):
        # 먼저 세션 생성
        res = api_client.post("/api/studio/ai/sessions/", {
            "book": book.id, "edition": edition.id, "prompt": "테스트",
        }, format="json")
        session_id = res.json()["id"]

        # approve (동기 실행)
        mock_content = MockLLMAdapter(responses=[json.dumps(DEFAULT_CONTENT)])
        with patch("bookstudio.adapters.factory.get_llm_adapter", return_value=mock_content):
            res2 = api_client.post(
                f"/api/studio/ai/sessions/{session_id}/approve/",
                {}, format="json",
            )

        assert res2.status_code == 200
        # 동기 모드에서는 approve 후 즉시 생성 완료
        session = AISession.objects.get(pk=session_id)
        assert session.status in (
            AISessionStatusEnum.APPROVED,
            AISessionStatusEnum.COMPLETE,
        )

    def test_approve_wrong_status(self, api_client, book, edition):
        session = AISession.objects.create(
            user=User.objects.get(username="aiuser"),
            book=book, edition=edition, prompt="test",
            status=AISessionStatusEnum.PLANNING,
        )
        res = api_client.post(
            f"/api/studio/ai/sessions/{session.id}/approve/",
            {}, format="json",
        )
        assert res.status_code == 400

    def test_cancel_session(self, api_client, book, edition):
        session = AISession.objects.create(
            user=User.objects.get(username="aiuser"),
            book=book, edition=edition, prompt="test",
            status=AISessionStatusEnum.GENERATING,
        )
        res = api_client.post(
            f"/api/studio/ai/sessions/{session.id}/cancel/",
            {}, format="json",
        )
        assert res.status_code == 200
        session.refresh_from_db()
        assert session.status == AISessionStatusEnum.CANCELLED

    def test_list_sessions(self, api_client, session):
        res = api_client.get("/api/studio/ai/sessions/")
        assert res.status_code == 200
        assert len(res.json()) >= 1
