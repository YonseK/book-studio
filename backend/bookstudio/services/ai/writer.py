"""콘텐츠 작성 서비스."""

from dataclasses import dataclass, field

from bookstudio.adapters.factory import get_llm_adapter
from bookstudio.services.ai.prompts.writer import WRITING_SYSTEM, WRITING_USER
from bookstudio.services.pattern_applicator import SlotContent


@dataclass
class PageContent:
    """AI가 생성한 페이지 콘텐츠."""

    slots: list[SlotContent] = field(default_factory=list)
    image_prompt: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0


class WriterService:
    """기획서 + 패턴 슬롯 → 슬롯별 콘텐츠 생성."""

    def __init__(self):
        self._previous_summaries: list[str] = []

    def generate_page_content(
        self,
        plan: dict,
        page_plan: dict,
        slot_roles: list[dict],
    ) -> PageContent:
        adapter = get_llm_adapter(task_type="writing")

        slot_roles_text = "\n".join(
            f"- {s['role']} ({s['media_type']})" for s in slot_roles
        )
        previous_summary = "\n".join(self._previous_summaries[-3:]) or "없음 (첫 페이지)"

        messages = [
            {"role": "system", "content": WRITING_SYSTEM},
            {"role": "user", "content": WRITING_USER.format(
                plan_title=plan.get("title", ""),
                plan_tone=plan.get("tone", ""),
                plan_audience=plan.get("target_audience", ""),
                page_index=page_plan["index"],
                total_pages=plan["total_pages"],
                page_role=page_plan["role"],
                page_purpose=page_plan["purpose"],
                key_points=", ".join(page_plan.get("key_points", [])),
                needs_image=page_plan.get("needs_image", False),
                slot_roles=slot_roles_text,
                previous_summary=previous_summary,
            )},
        ]

        data, in_tok, out_tok = adapter.generate_json(
            messages=messages, temperature=0.5, max_tokens=2000,
        )

        slots = [
            SlotContent(
                role=s["role"],
                text=s.get("text", ""),
                headline=s.get("headline", ""),
                document_html=s.get("document_html"),
            )
            for s in data.get("slots", [])
        ]

        self._previous_summaries.append(
            f"[{page_plan['role']}] {page_plan['purpose']}"
        )

        return PageContent(
            slots=slots,
            image_prompt=data.get("image_prompt"),
            input_tokens=in_tok,
            output_tokens=out_tok,
        )

    def reset(self):
        self._previous_summaries = []
