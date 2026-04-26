"""기획서 생성 서비스."""

import json
from dataclasses import dataclass, field

from bookstudio.adapters.factory import get_llm_adapter
from bookstudio.services.ai.prompts.planner import PLANNING_SYSTEM, PLANNING_USER
from bookstudio.services.layout import get_layout


@dataclass
class Plan:
    title: str
    total_pages: int
    tone: str
    target_audience: str
    color_mood: str
    pages: list[dict] = field(default_factory=list)
    raw: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "Plan":
        return cls(
            title=data.get("title", ""),
            total_pages=data.get("total_pages", 0),
            tone=data.get("tone", ""),
            target_audience=data.get("target_audience", ""),
            color_mood=data.get("color_mood", "dark"),
            pages=data.get("pages", []),
            raw=data,
        )


class PlannerService:
    """사용자 프롬프트 → 기획서 JSON 생성."""

    def generate_plan(
        self,
        prompt: str,
        layout_preset: str,
        options: dict | None = None,
    ) -> tuple[Plan, int, int]:
        """Returns: (plan, input_tokens, output_tokens)"""
        adapter = get_llm_adapter(task_type="planning")
        layout = get_layout(layout_preset)

        options = options or {}
        options_text = ""
        if options.get("page_count"):
            options_text += f"페이지 수: {options['page_count']}매\n"
        if options.get("tone"):
            options_text += f"톤: {options['tone']}\n"
        if options.get("language"):
            options_text += f"언어: {options['language']}\n"

        messages = [
            {"role": "system", "content": PLANNING_SYSTEM},
            {"role": "user", "content": PLANNING_USER.format(
                prompt=prompt,
                layout_label=layout.label,
                layout_width=layout.width,
                layout_height=layout.height,
                options_text=options_text,
            )},
        ]

        data, in_tok, out_tok = adapter.generate_json(
            messages=messages, temperature=0.3, max_tokens=4000,
        )
        return Plan.from_dict(data), in_tok, out_tok
