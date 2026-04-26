"""AI 북 생성 전체 파이프라인 조율."""

import logging

from bookstudio.models.ai import AISession, AISessionStatusEnum
from bookstudio.services.ai.planner import PlannerService
from bookstudio.services.ai.writer import WriterService
from bookstudio.services.ai.designer import DesignerService
from bookstudio.services.pattern_applicator import PatternApplicator
from bookstudio.services.layout import get_layout

logger = logging.getLogger(__name__)


class OrchestratorService:
    """AI 북 생성 전체 파이프라인 조율."""

    def __init__(self, event_callback=None):
        self.planner = PlannerService()
        self.writer = WriterService()
        self.designer = DesignerService()
        self.applicator = PatternApplicator()
        self.emit = event_callback or (lambda t, d: None)

    def run_planning(self, session: AISession) -> dict:
        """기획서 생성."""
        self.emit("planning_start", {"session_id": session.id})

        plan, in_tok, out_tok = self.planner.generate_plan(
            prompt=session.prompt,
            layout_preset=session.book.book_layout,
            options=session.options,
        )

        session.plan = plan.raw
        session.total_pages = plan.total_pages
        session.status = AISessionStatusEnum.REVIEW
        session.model_used = "planning"
        session.save(update_fields=[
            "plan", "total_pages", "status", "model_used", "updated_at",
        ])
        session.add_token_usage(in_tok, out_tok)

        self.emit("planning_complete", {
            "session_id": session.id,
            "plan": plan.raw,
        })

        return plan.raw

    def run_generation(self, session: AISession):
        """기획서 승인 후 콘텐츠 + 디자인 생성."""
        # 순환 임포트 방지: 런타임에 로드
        from bookstudio.api.serializers.page import PageSerializer
        from bookstudio.api.serializers.panel import PanelSerializer

        plan = session.plan
        layout = get_layout(session.book.book_layout)

        pattern_set = session.pattern_set or self.designer.select_pattern_set(plan)
        used_pattern_ids: list[str] = []
        self.writer.reset()

        existing_page_count = session.edition.pages.filter(deleted=False).count()

        session.status = AISessionStatusEnum.GENERATING
        session.save(update_fields=["status", "updated_at"])

        self.emit("generation_start", {
            "session_id": session.id,
            "total_pages": plan["total_pages"],
        })

        for page_plan in plan["pages"]:
            page_index = page_plan["index"]

            try:
                self.emit("page_start", {
                    "session_id": session.id,
                    "page_index": page_index,
                    "page_role": page_plan["role"],
                })

                # 1. 패턴 선택
                pattern = self.designer.select_pattern(
                    page_plan=page_plan,
                    pattern_set=pattern_set,
                    used_pattern_ids=used_pattern_ids,
                )
                used_pattern_ids.append(pattern.id)

                # 2. 슬롯 정보
                slot_roles = [
                    {"role": s.role, "media_type": s.media_type}
                    for s in pattern.slots.order_by("order")
                ]

                # 3. 콘텐츠 생성
                page_content = self.writer.generate_page_content(
                    plan=plan,
                    page_plan=page_plan,
                    slot_roles=slot_roles,
                )

                # 4. 패턴 적용
                palette_override = (
                    pattern_set.palette
                    if pattern_set and pattern_set.palette
                    else None
                )
                result = self.applicator.apply(
                    pattern=pattern,
                    layout=layout,
                    contents=page_content.slots,
                    edition_id=str(session.edition_id),
                    user_id=str(session.user_id),
                    page_order=existing_page_count + page_index,
                    palette_override=palette_override,
                )

                # 5. 토큰 기록
                session.add_token_usage(
                    page_content.input_tokens, page_content.output_tokens,
                )

                # 6. 진행률
                session.increment_progress()

                self.emit("page_complete", {
                    "session_id": session.id,
                    "page_index": page_index,
                    "page": PageSerializer(result.page).data,
                    "panels": PanelSerializer(result.panels, many=True).data,
                })

            except Exception as e:
                logger.error(
                    f"Page {page_index} generation failed: {e}", exc_info=True
                )
                self.emit("page_error", {
                    "session_id": session.id,
                    "page_index": page_index,
                    "error": str(e),
                })
                continue

        session.mark_complete()
        self.emit("generation_complete", {
            "session_id": session.id,
            "completed_pages": session.completed_pages,
        })
