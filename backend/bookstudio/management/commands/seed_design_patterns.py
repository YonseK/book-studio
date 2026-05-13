"""GenSpark 슬라이드 역설계 기반 고품질 디자인 패턴 시드.

12개 패턴 + midnight_indigo 패턴 세트를 생성한다.
이미 존재하는 패턴(name 기준)은 건너뛴다.

사용법:
    python manage.py seed_design_patterns
    python manage.py seed_design_patterns --flush   # 기존 시드 패턴 삭제 후 재생성
"""

from django.core.management.base import BaseCommand

from bookstudio.models.design_pattern import (
    DesignPattern,
    DesignPatternSet,
    DesignPatternSetMembership,
    DesignPatternSlot,
)

# ─────────────────────────────────────────────────────────────
# 공통 팔레트
# ─────────────────────────────────────────────────────────────
MIDNIGHT_INDIGO = {
    "background": "#0a0a0f",
    "background_gradient": "linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%)",
    "text": "#ffffff",
    "primary": "#6366f1",
    "accent": "#8b5cf6",
    "accent2": "#a855f7",
    "secondary": "rgba(255,255,255,0.6)",
    "muted": "rgba(255,255,255,0.4)",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "card_bg": "rgba(255,255,255,0.04)",
    "card_border": "rgba(255,255,255,0.1)",
}

TYPOGRAPHY = {
    "heading_font": "Noto Sans KR",
    "body_font": "Noto Sans KR",
    "heading_size": 28,
}

# ─────────────────────────────────────────────────────────────
# 공통 슬롯 스타일 헬퍼
# ─────────────────────────────────────────────────────────────
_CARD = {
    "background_color": "rgba(255,255,255,0.04)",
    "border_width": 1,
    "border_color": "rgba(255,255,255,0.1)",
    "border_radius": 16,
}

_HEADER_STYLE = {
    "font_size": 13,
    "color": "rgba(255,255,255,0.4)",
}

_FOOTER_STYLE = {
    "font_size": 13,
    "color": "rgba(255,255,255,0.4)",
}


def _header_slot(order=0):
    return {
        "role": "header",
        "media_type": "TXT",
        "left_pct": 5, "top_pct": 4.4, "width_pct": 90, "height_pct": 3.3,
        "style": _HEADER_STYLE,
        "order": order,
    }


def _footer_slot(order=99):
    return {
        "role": "footer",
        "media_type": "TXT",
        "left_pct": 5, "top_pct": 95.6, "width_pct": 90, "height_pct": 3.3,
        "style": _FOOTER_STYLE,
        "order": order,
    }


# ─────────────────────────────────────────────────────────────
# 12개 패턴 정의
# ─────────────────────────────────────────────────────────────
PATTERNS = [
    # ── 1. TITLE: 히어로 표지 ──
    {
        "name": "title_hero_dark",
        "description": "다크 히어로 표지 — 중앙 로고, 그라디언트 슬로건, KPI 카드 3개, 상태 뱃지",
        "category": "TITLE",
        "tags": ["hero", "dark", "kpi", "brand"],
        "slots": [
            _header_slot(0),
            {"role": "icon_box", "media_type": "SHA", "left_pct": 39.1, "top_pct": 16.7, "width_pct": 21.9, "height_pct": 13.9,
             "style": {"background_color": "linear-gradient(135deg, #6366f1, #8b5cf6)", "border_radius": 22}, "order": 1},
            {"role": "title", "media_type": "HL", "left_pct": 14.8, "top_pct": 34, "width_pct": 70.3, "height_pct": 7,
             "style": {"font_size": 36, "font_weight": "800", "text_align": "center"}, "order": 2},
            {"role": "subtitle", "media_type": "TXT", "left_pct": 14.8, "top_pct": 42, "width_pct": 70.3, "height_pct": 12,
             "style": {"font_size": 20, "text_align": "center", "line_height": 1.7}, "order": 3},
            {"role": "stat_value", "media_type": "TXT", "left_pct": 20.3, "top_pct": 58.3, "width_pct": 17.2, "height_pct": 19.4,
             "style": {**_CARD, "font_size": 32, "font_weight": "800"}, "order": 4},
            {"role": "stat_value", "media_type": "TXT", "left_pct": 39.5, "top_pct": 58.3, "width_pct": 17.2, "height_pct": 19.4,
             "style": {**_CARD, "font_size": 32, "font_weight": "800"}, "order": 5},
            {"role": "stat_value", "media_type": "TXT", "left_pct": 58.6, "top_pct": 58.3, "width_pct": 17.2, "height_pct": 19.4,
             "style": {**_CARD, "font_size": 32, "font_weight": "800"}, "order": 6},
            {"role": "badge", "media_type": "TXT", "left_pct": 30.5, "top_pct": 82.6, "width_pct": 39.1, "height_pct": 5.6,
             "style": {"font_size": 15, "font_weight": "600"}, "order": 7},
            _footer_slot(8),
        ],
    },
    # ── 2. TWO_COLUMN: Executive Summary ──
    {
        "name": "exec_summary_two_col",
        "description": "좌측 핵심 개념(아이콘 리스트+태그) / 우측 현재 상태(메트릭+프로그레스바)",
        "category": "CONTENT_2COL",
        "tags": ["summary", "two-col", "metrics", "progress"],
        "slots": [
            {"role": "header", "media_type": "TXT", "left_pct": 5, "top_pct": 4.4, "width_pct": 90, "height_pct": 5.6,
             "style": {"font_size": 28, "font_weight": "700"}, "order": 0},
            {"role": "card", "media_type": "SHA", "left_pct": 5, "top_pct": 12.5, "width_pct": 43, "height_pct": 77.8,
             "style": _CARD, "order": 1},
            {"role": "card", "media_type": "SHA", "left_pct": 50.5, "top_pct": 12.5, "width_pct": 43, "height_pct": 77.8,
             "style": _CARD, "order": 2},
            _footer_slot(3),
        ],
    },
    # ── 3. THREE_COLUMN: 문제 정의 ──
    {
        "name": "problem_three_col",
        "description": "3단 색상코딩 카드(심각도별) + 하단 인사이트 요약 바",
        "category": "THREE_COL",
        "tags": ["problem", "three-col", "severity", "insight"],
        "slots": [
            {"role": "header", "media_type": "TXT", "left_pct": 5, "top_pct": 4.4, "width_pct": 90, "height_pct": 8.3,
             "style": {"font_size": 28, "font_weight": "800"}, "order": 0},
            {"role": "card", "media_type": "SHA", "left_pct": 5, "top_pct": 13.9, "width_pct": 28.4, "height_pct": 68.1,
             "style": _CARD, "order": 1},
            {"role": "card", "media_type": "SHA", "left_pct": 35.3, "top_pct": 13.9, "width_pct": 28.4, "height_pct": 68.1,
             "style": _CARD, "order": 2},
            {"role": "card", "media_type": "SHA", "left_pct": 65.6, "top_pct": 13.9, "width_pct": 28.4, "height_pct": 68.1,
             "style": _CARD, "order": 3},
            {"role": "summary", "media_type": "SHA", "left_pct": 5, "top_pct": 84, "width_pct": 90, "height_pct": 9.2,
             "style": {**_CARD, "border_radius": 12}, "order": 4},
            _footer_slot(5),
        ],
    },
    # ── 4. TWO_COLUMN: 해결책 ──
    {
        "name": "solution_two_col",
        "description": "좌측 Orchestrator(설명+원리 리스트) / 우측 MU:DAM(2×2 그리드+인용+경고)",
        "category": "CONTENT_2COL",
        "tags": ["solution", "two-col", "grid", "warning"],
        "slots": [
            {"role": "header", "media_type": "TXT", "left_pct": 5, "top_pct": 4.4, "width_pct": 90, "height_pct": 5.6,
             "style": {"font_size": 32, "font_weight": "700"}, "order": 0},
            {"role": "card", "media_type": "SHA", "left_pct": 5, "top_pct": 13.9, "width_pct": 43, "height_pct": 75,
             "style": _CARD, "order": 1},
            {"role": "card", "media_type": "SHA", "left_pct": 50.5, "top_pct": 13.9, "width_pct": 43, "height_pct": 75,
             "style": _CARD, "order": 2},
            _footer_slot(3),
        ],
    },
    # ── 5. FLOW: 시스템 아키텍처 ──
    {
        "name": "architecture_flow",
        "description": "상단 5노드 수평 플로우(화살표) + 하단 2단(번호 리스트 / 2×2 특성 그리드)",
        "category": "FLOW",
        "tags": ["architecture", "flow", "pipeline", "steps"],
        "slots": [
            {"role": "header", "media_type": "TXT", "left_pct": 5, "top_pct": 4.4, "width_pct": 90, "height_pct": 5.6,
             "style": {"font_size": 24, "font_weight": "700"}, "order": 0},
            {"role": "flow_node", "media_type": "SHA", "left_pct": 5, "top_pct": 13.9, "width_pct": 90, "height_pct": 27.8,
             "style": {}, "order": 1},
            {"role": "card", "media_type": "SHA", "left_pct": 5, "top_pct": 45, "width_pct": 43, "height_pct": 50.6,
             "style": _CARD, "order": 2},
            {"role": "card", "media_type": "SHA", "left_pct": 50.5, "top_pct": 45, "width_pct": 43, "height_pct": 50.6,
             "style": _CARD, "order": 3},
            _footer_slot(4),
        ],
    },
    # ── 6. GRID_CARDS: 에이전트 그리드 ──
    {
        "name": "agent_grid_cards",
        "description": "4+3 에이전트 카드 그리드(마지막 더블폭) + 통계 바 3개",
        "category": "GRID_CARDS",
        "tags": ["grid", "agent", "cards", "stats"],
        "slots": [
            {"role": "header", "media_type": "TXT", "left_pct": 5, "top_pct": 4.4, "width_pct": 90, "height_pct": 8.3,
             "style": {"font_size": 24, "font_weight": "800"}, "order": 0},
            # Row 1: 4 cards
            {"role": "card", "media_type": "SHA", "left_pct": 5, "top_pct": 15.3, "width_pct": 21, "height_pct": 25,
             "style": _CARD, "order": 1},
            {"role": "card", "media_type": "SHA", "left_pct": 27.5, "top_pct": 15.3, "width_pct": 21, "height_pct": 25,
             "style": _CARD, "order": 2},
            {"role": "card", "media_type": "SHA", "left_pct": 50, "top_pct": 15.3, "width_pct": 21, "height_pct": 25,
             "style": _CARD, "order": 3},
            {"role": "card", "media_type": "SHA", "left_pct": 72.5, "top_pct": 15.3, "width_pct": 21, "height_pct": 25,
             "style": _CARD, "order": 4},
            # Row 2: 3 cards (last one double width)
            {"role": "card", "media_type": "SHA", "left_pct": 5, "top_pct": 42.5, "width_pct": 21, "height_pct": 25,
             "style": _CARD, "order": 5},
            {"role": "card", "media_type": "SHA", "left_pct": 27.5, "top_pct": 42.5, "width_pct": 21, "height_pct": 25,
             "style": _CARD, "order": 6},
            {"role": "card", "media_type": "SHA", "left_pct": 50, "top_pct": 42.5, "width_pct": 43.5, "height_pct": 25,
             "style": {**_CARD, "background_color": "rgba(99,102,241,0.08)", "border_color": "rgba(99,102,241,0.3)"}, "order": 7},
            # Stats row
            {"role": "stat_value", "media_type": "TXT", "left_pct": 5, "top_pct": 69.9, "width_pct": 28, "height_pct": 11.1,
             "style": {**_CARD, "border_radius": 12}, "order": 8},
            {"role": "stat_value", "media_type": "TXT", "left_pct": 35, "top_pct": 69.9, "width_pct": 28, "height_pct": 11.1,
             "style": {**_CARD, "border_radius": 12}, "order": 9},
            {"role": "stat_value", "media_type": "TXT", "left_pct": 65, "top_pct": 69.9, "width_pct": 28, "height_pct": 11.1,
             "style": {**_CARD, "border_radius": 12}, "order": 10},
            _footer_slot(11),
        ],
    },
    # ── 7. GRID_CARDS: MU:DAM 양심기관 ──
    {
        "name": "mudam_conscience_gate",
        "description": "상단 2열(4가지 권한 + 양심 질문) + 하단 풀폭 4열 게이팅 트리거",
        "category": "GRID_CARDS",
        "tags": ["mudam", "conscience", "gate", "triggers"],
        "slots": [
            {"role": "header", "media_type": "TXT", "left_pct": 5, "top_pct": 4.4, "width_pct": 90, "height_pct": 8.3,
             "style": {"font_size": 28, "font_weight": "800"}, "order": 0},
            {"role": "card", "media_type": "SHA", "left_pct": 5, "top_pct": 15.6, "width_pct": 42.2, "height_pct": 41.7,
             "style": _CARD, "order": 1},
            {"role": "card", "media_type": "SHA", "left_pct": 48.8, "top_pct": 15.6, "width_pct": 46.3, "height_pct": 41.7,
             "style": _CARD, "order": 2},
            {"role": "card", "media_type": "SHA", "left_pct": 5, "top_pct": 60, "width_pct": 90, "height_pct": 25,
             "style": _CARD, "order": 3},
            {"role": "summary", "media_type": "SHA", "left_pct": 5, "top_pct": 87.8, "width_pct": 90, "height_pct": 7.8,
             "style": {**_CARD, "background_color": "rgba(255,255,255,0.06)", "border_color": "rgba(255,255,255,0.15)", "border_radius": 12}, "order": 4},
        ],
    },
    # ── 8. THREE_COLUMN: 자율 운영 3단계 ──
    {
        "name": "autonomy_three_tier",
        "description": "L1/L2/L3 수직 카드 + 화살표, 각각 프로그레스바·감시미터·예시목록",
        "category": "THREE_COL",
        "tags": ["autonomy", "tier", "level", "progress"],
        "slots": [
            {"role": "header", "media_type": "TXT", "left_pct": 5, "top_pct": 4.4, "width_pct": 90, "height_pct": 8.3,
             "style": {"font_size": 26, "font_weight": "800"}, "order": 0},
            {"role": "card", "media_type": "SHA", "left_pct": 5, "top_pct": 13.9, "width_pct": 28.1, "height_pct": 73.6,
             "style": {**_CARD, "border_color": "rgba(34,197,94,0.3)"}, "order": 1},
            {"role": "card", "media_type": "SHA", "left_pct": 35.8, "top_pct": 13.9, "width_pct": 28.1, "height_pct": 73.6,
             "style": {**_CARD, "border_color": "rgba(245,158,11,0.3)"}, "order": 2},
            {"role": "card", "media_type": "SHA", "left_pct": 66.6, "top_pct": 13.9, "width_pct": 28.1, "height_pct": 73.6,
             "style": {**_CARD, "border_color": "rgba(239,68,68,0.3)"}, "order": 3},
            _footer_slot(4),
        ],
    },
    # ── 9. THREE_COLUMN: 타겟 시장 ──
    {
        "name": "target_market_three_stage",
        "description": "3단 시장(위기관리/AI어시스턴트/딜인텔) + 하단 요약 바",
        "category": "THREE_COL",
        "tags": ["market", "three-col", "strategy", "stages"],
        "slots": [
            {"role": "header", "media_type": "TXT", "left_pct": 5, "top_pct": 4.4, "width_pct": 90, "height_pct": 8.3,
             "style": {"font_size": 28, "font_weight": "800"}, "order": 0},
            {"role": "card", "media_type": "SHA", "left_pct": 5, "top_pct": 13.3, "width_pct": 28.8, "height_pct": 73.6,
             "style": _CARD, "order": 1},
            {"role": "card", "media_type": "SHA", "left_pct": 35.6, "top_pct": 13.3, "width_pct": 28.8, "height_pct": 73.6,
             "style": _CARD, "order": 2},
            {"role": "card", "media_type": "SHA", "left_pct": 66.3, "top_pct": 13.3, "width_pct": 28.8, "height_pct": 73.6,
             "style": _CARD, "order": 3},
            {"role": "summary", "media_type": "SHA", "left_pct": 5, "top_pct": 88.3, "width_pct": 90, "height_pct": 8.3,
             "style": {**_CARD, "border_radius": 12}, "order": 4},
            _footer_slot(5),
        ],
    },
    # ── 10. PRICING: 비즈니스 모델 ──
    {
        "name": "business_model_pricing",
        "description": "수익구조 요약 + 3열 프라이싱 카드(Starter/Pro/Enterprise)",
        "category": "PRICING",
        "tags": ["pricing", "plans", "revenue", "business"],
        "slots": [
            {"role": "header", "media_type": "TXT", "left_pct": 5, "top_pct": 4.4, "width_pct": 90, "height_pct": 11.1,
             "style": {"font_size": 32, "font_weight": "800"}, "order": 0},
            {"role": "summary", "media_type": "SHA", "left_pct": 5, "top_pct": 16.7, "width_pct": 90, "height_pct": 13.9,
             "style": {**_CARD, "border_radius": 16}, "order": 1},
            {"role": "card", "media_type": "SHA", "left_pct": 5, "top_pct": 33.3, "width_pct": 28.8, "height_pct": 62.5,
             "style": _CARD, "order": 2},
            {"role": "card", "media_type": "SHA", "left_pct": 35.6, "top_pct": 33.3, "width_pct": 28.8, "height_pct": 62.5,
             "style": {**_CARD, "border_width": 2, "border_color": "rgba(139,92,246,0.3)"}, "order": 3},
            {"role": "card", "media_type": "SHA", "left_pct": 66.3, "top_pct": 33.3, "width_pct": 28.8, "height_pct": 62.5,
             "style": _CARD, "order": 4},
        ],
    },
    # ── 11. TWO_COLUMN: 경쟁 우위 ──
    {
        "name": "competitive_advantage",
        "description": "좌측 2×3 기술해자 그리드+비교표 / 우측 4사분면 매트릭스+스탯",
        "category": "CONTENT_2COL",
        "tags": ["competitive", "moat", "matrix", "chart"],
        "slots": [
            {"role": "header", "media_type": "TXT", "left_pct": 5, "top_pct": 4.4, "width_pct": 90, "height_pct": 8.9,
             "style": {"font_size": 28, "font_weight": "800"}, "order": 0},
            {"role": "card", "media_type": "SHA", "left_pct": 5, "top_pct": 15, "width_pct": 43.8, "height_pct": 75,
             "style": _CARD, "order": 1},
            {"role": "card", "media_type": "SHA", "left_pct": 51.3, "top_pct": 15, "width_pct": 43.8, "height_pct": 75,
             "style": _CARD, "order": 2},
            _footer_slot(3),
        ],
    },
    # ── 12. TIMELINE: 투자 하이라이트 & 마일스톤 ──
    {
        "name": "investment_milestones",
        "description": "상단 3열 카드(Why Us/기술완성도/기업가치) + 하단 5열 타임라인 로드맵",
        "category": "TIMELINE",
        "tags": ["investment", "milestones", "roadmap", "timeline"],
        "slots": [
            {"role": "header", "media_type": "TXT", "left_pct": 5, "top_pct": 3.9, "width_pct": 90, "height_pct": 5.6,
             "style": {"font_size": 24, "font_weight": "700"}, "order": 0},
            # Top 3 cards
            {"role": "card", "media_type": "SHA", "left_pct": 5, "top_pct": 11.1, "width_pct": 28.9, "height_pct": 28.1,
             "style": _CARD, "order": 1},
            {"role": "card", "media_type": "SHA", "left_pct": 35.5, "top_pct": 11.1, "width_pct": 28.9, "height_pct": 28.1,
             "style": _CARD, "order": 2},
            {"role": "card", "media_type": "SHA", "left_pct": 65.9, "top_pct": 11.1, "width_pct": 28.9, "height_pct": 28.1,
             "style": _CARD, "order": 3},
            # Timeline card (full width bottom)
            {"role": "card", "media_type": "SHA", "left_pct": 5, "top_pct": 41.4, "width_pct": 90, "height_pct": 55.3,
             "style": _CARD, "order": 4},
            _footer_slot(5),
        ],
    },
]


class Command(BaseCommand):
    help = "GenSpark 역설계 기반 고품질 디자인 패턴 12개 + midnight_indigo 패턴 세트 시드"

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="기존 시드 패턴(source=CURATED, name 매칭)을 삭제 후 재생성",
        )

    def handle(self, *args, **options):
        seed_names = {p["name"] for p in PATTERNS}

        if options["flush"]:
            deleted, _ = DesignPattern.objects.filter(
                name__in=seed_names, source="CURATED"
            ).delete()
            self.stdout.write(f"  기존 시드 패턴 {deleted}건 삭제")

        created = 0
        skipped = 0
        patterns_by_name: dict[str, DesignPattern] = {}

        for pdef in PATTERNS:
            name = pdef["name"]
            if DesignPattern.objects.filter(name=name).exists():
                patterns_by_name[name] = DesignPattern.objects.get(name=name)
                skipped += 1
                continue

            slots_data = pdef.pop("slots")
            pattern = DesignPattern.objects.create(
                name=name,
                description=pdef["description"],
                category=pdef["category"],
                tags=pdef.get("tags", []),
                target_layout="PPTX_WIDE",
                page_background_type="CLR",
                page_background_color="#0a0a0f",
                page_opacity=1.0,
                palette=MIDNIGHT_INDIGO,
                typography=TYPOGRAPHY,
                source="CURATED",
            )

            for slot_data in slots_data:
                DesignPatternSlot.objects.create(
                    pattern=pattern,
                    role=slot_data["role"],
                    media_type=slot_data.get("media_type", "TXT"),
                    left_pct=slot_data["left_pct"],
                    top_pct=slot_data["top_pct"],
                    width_pct=slot_data["width_pct"],
                    height_pct=slot_data["height_pct"],
                    style=slot_data.get("style", {}),
                    order=slot_data.get("order", 0),
                )

            patterns_by_name[name] = pattern
            created += 1
            self.stdout.write(f"  ✓ {name} ({pdef['category']}) — {len(slots_data)}개 슬롯")

        self.stdout.write(
            self.style.SUCCESS(f"\n패턴: {created}개 생성, {skipped}개 스킵")
        )

        # ── 패턴 세트: midnight_indigo ──
        set_name = "Midnight Indigo"
        pset, pset_created = DesignPatternSet.objects.get_or_create(
            name=set_name,
            defaults={
                "description": "다크 인디고 테마 — GenSpark 스타일 12개 패턴 세트",
                "palette": MIDNIGHT_INDIGO,
                "target_layout": "PPTX_WIDE",
            },
        )

        if pset_created:
            for i, pdef in enumerate(PATTERNS):
                pattern = patterns_by_name.get(pdef["name"])
                if pattern:
                    DesignPatternSetMembership.objects.get_or_create(
                        pattern_set=pset,
                        pattern=pattern,
                        defaults={"priority": i},
                    )
            self.stdout.write(
                self.style.SUCCESS(f"패턴 세트: '{set_name}' 생성 ({len(PATTERNS)}개 패턴 연결)")
            )
        else:
            self.stdout.write(f"패턴 세트: '{set_name}' 이미 존재 — 스킵")
