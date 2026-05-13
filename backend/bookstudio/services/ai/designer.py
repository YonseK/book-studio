"""디자인 패턴 선택 서비스."""

import json
import logging

from bookstudio.adapters.factory import get_llm_adapter
from bookstudio.models.design_pattern import (
    DesignPattern,
    DesignPatternSet,
    PatternCategoryEnum,
)
from bookstudio.services.ai.prompts.designer import (
    PATTERN_SELECTION_SYSTEM,
    PATTERN_SELECTION_USER,
)

logger = logging.getLogger(__name__)


class DesignerService:
    """페이지 기획 + 패턴 세트 → 최적 패턴 선택."""

    # 신규 카테고리 → 유사 기존 카테고리 fallback 매핑
    _CATEGORY_FALLBACK = {
        "STATS": "DATA",
        "THREE_COL": "COMPARISON",
        "GRID_CARDS": "CONTENT",
        "FLOW": "CONTENT_2COL",
        "TIMELINE": "CLOSING",
        "CHART": "DATA",
        "PRICING": "COMPARISON",
    }

    def select_pattern(
        self,
        page_plan: dict,
        pattern_set: DesignPatternSet | None,
        used_pattern_ids: list[str],
        available_patterns: list[DesignPattern] | None = None,
    ) -> DesignPattern:
        category = page_plan.get("suggested_pattern_category", "CONTENT")

        # 1단계: 패턴 세트에서 직접 매칭
        if pattern_set:
            pattern = pattern_set.get_pattern(category)
            if pattern and pattern.id not in used_pattern_ids:
                return pattern

        # 2단계: LLM 선택
        candidates = available_patterns or self._get_candidates(category)
        if len(candidates) > 1:
            pattern = self._llm_select(page_plan, candidates, used_pattern_ids)
            if pattern:
                return pattern

        # 3단계: 직접 카테고리 fallback
        if candidates:
            # 미사용 패턴 우선
            unused = [p for p in candidates if p.id not in used_pattern_ids]
            return unused[0] if unused else candidates[0]

        # 4단계: 유사 카테고리 fallback
        fallback_cat = self._CATEGORY_FALLBACK.get(category)
        if fallback_cat:
            if pattern_set:
                fb = pattern_set.get_pattern(fallback_cat)
                if fb:
                    return fb
            fb_candidates = self._get_candidates(fallback_cat)
            if fb_candidates:
                return fb_candidates[0]

        # 5단계: CONTENT fallback
        fallback = DesignPattern.objects.filter(
            category=PatternCategoryEnum.CONTENT, is_active=True
        ).first()
        if fallback:
            return fallback

        # 최후 fallback — 아무 활성 패턴
        return DesignPattern.objects.filter(is_active=True).first()

    def select_pattern_set(self, plan: dict) -> DesignPatternSet | None:
        # TODO: Phase 4에서 color_mood 기반 매칭 고도화
        return DesignPatternSet.objects.filter(is_active=True).first()

    def _get_candidates(self, category: str) -> list[DesignPattern]:
        return list(
            DesignPattern.objects.filter(
                category=category, is_active=True
            ).prefetch_related("slots").order_by("-usage_count")[:5]
        )

    def _llm_select(
        self, page_plan: dict, candidates: list[DesignPattern], used_ids: list[str]
    ) -> DesignPattern | None:
        try:
            adapter = get_llm_adapter(task_type="design")
            patterns_json = [
                {
                    "id": p.id,
                    "name": p.name,
                    "category": p.category,
                    "slots": [
                        {"role": s.role, "media_type": s.media_type}
                        for s in p.slots.all()
                    ],
                }
                for p in candidates
            ]

            messages = [
                {"role": "system", "content": PATTERN_SELECTION_SYSTEM},
                {"role": "user", "content": PATTERN_SELECTION_USER.format(
                    page_role=page_plan.get("role", ""),
                    page_purpose=page_plan.get("purpose", ""),
                    needs_image=page_plan.get("needs_image", False),
                    patterns_json=json.dumps(patterns_json, ensure_ascii=False),
                    used_patterns=json.dumps(used_ids),
                )},
            ]

            data, _, _ = adapter.generate_json(messages=messages, temperature=0.1)
            selected_id = data.get("pattern_id")
            return next((p for p in candidates if p.id == selected_id), None)
        except Exception:
            logger.warning("LLM pattern selection failed, using fallback", exc_info=True)
            return None
