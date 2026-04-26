"""기존 북 데이터에서 디자인 패턴을 추출하는 관리 커맨드."""

import logging
from collections import Counter

from django.core.management.base import BaseCommand
from django.db import models as db_models
from django.db.models import Count

from bookstudio.models import Page, Panel, MediaTypeEnum
from bookstudio.models.design_pattern import (
    DesignPattern,
    DesignPatternSlot,
    PatternCategoryEnum,
    PatternSourceEnum,
    SlotRoleEnum,
)
from bookstudio.services.layout import get_layout, LAYOUT_PRESETS

logger = logging.getLogger(__name__)

# Panel 스타일 필드 중 추출할 것들
STYLE_EXTRACT_FIELDS = [
    "font_size", "font_family", "font_weight", "font_style",
    "font_bold", "font_italic", "color", "text_align",
    "letter_spacing", "line_height",
    "background_color", "background_opacity", "padding",
    "border_width", "border_radius", "border_color",
    "opacity", "shape_type",
]

# Panel 모델의 기본값 (기본값과 같으면 추출하지 않음)
PANEL_DEFAULTS = {
    "font_size": 16,
    "font_family": "initial",
    "font_weight": "initial",
    "font_style": "initial",
    "font_bold": False,
    "font_italic": False,
    "color": "#ffffff",
    "text_align": "initial",
    "letter_spacing": 0.0,
    "line_height": 1.0,
    "background_color": "transparent",
    "background_opacity": 1.0,
    "padding": 0,
    "border_width": 0,
    "border_radius": 0,
    "border_color": "#ffffff",
    "opacity": 1.0,
    "shape_type": 0,
}


class Command(BaseCommand):
    help = "기존 북 데이터에서 디자인 패턴을 추출"

    def add_arguments(self, parser):
        parser.add_argument(
            "--book-layout", default="PPTX_WIDE",
            help="대상 레이아웃 (default: PPTX_WIDE)",
        )
        parser.add_argument(
            "--book-id", default=None,
            help="특정 북에서만 추출",
        )
        parser.add_argument(
            "--min-panels", type=int, default=2,
            help="최소 패널 수 (default: 2)",
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="DB 저장 없이 결과만 출력",
        )

    def handle(self, **options):
        layout_preset = options["book_layout"]
        layout = get_layout(layout_preset)
        min_panels = options["min_panels"]
        dry_run = options["dry_run"]

        pages = self._collect_pages(options, layout_preset, min_panels)
        self.stdout.write(f"대상 페이지: {len(pages)}개")

        raw_patterns = []
        for page in pages:
            panels = list(
                page.panels.filter(deleted=False, is_active=True).order_by("order")
            )
            if len(panels) < min_panels:
                continue
            extracted = self._extract_from_page(page, panels, layout)
            if extracted:
                raw_patterns.append(extracted)

        self.stdout.write(f"추출된 원시 패턴: {len(raw_patterns)}개")

        deduplicated = self._deduplicate(raw_patterns)
        self.stdout.write(f"중복 제거 후: {len(deduplicated)}개")

        if dry_run:
            for p in deduplicated:
                self.stdout.write(
                    f"  [{p['category']}] {len(p['slots'])}슬롯 "
                    f"- 페이지 {p['source_page_id'][:8]}"
                )
        else:
            saved = self._save_patterns(deduplicated, layout_preset)
            self.stdout.write(self.style.SUCCESS(f"저장 완료: {saved}개 패턴"))

    def _collect_pages(self, options, layout_preset, min_panels):
        qs = Page.objects.filter(
            deleted=False, is_active=True,
            book_edition__book__book_layout=layout_preset,
        ).annotate(
            panel_count=Count("panels", filter=db_models.Q(panels__deleted=False))
        ).filter(
            panel_count__gte=min_panels,
        ).select_related("book_edition__book")

        if options["book_id"]:
            qs = qs.filter(book_edition__book_id=options["book_id"])

        return list(qs[:500])  # 최대 500 페이지

    def _extract_from_page(self, page, panels, layout):
        slots = []
        for panel in panels:
            role = self._infer_role(panel, layout)
            coords = self._normalize_coords(panel, layout)
            style = self._extract_style(panel)
            slots.append({
                "role": role,
                "media_type": panel.media_type,
                **coords,
                "style": style,
            })

        # 카테고리 추론
        category = self._infer_category(slots)

        # 팔레트 추출
        palette = self._extract_palette(page, panels)

        return {
            "category": category,
            "slots": slots,
            "palette": palette,
            "page_background_color": page.background_color,
            "page_background_type": page.background_type,
            "page_opacity": page.opacity,
            "source_page_id": str(page.id),
        }

    def _infer_role(self, panel, layout):
        if panel.media_type == MediaTypeEnum.HL:
            return SlotRoleEnum.TITLE if panel.font_size >= 28 else SlotRoleEnum.SUBTITLE

        if panel.media_type == MediaTypeEnum.IMG:
            return SlotRoleEnum.IMAGE

        if panel.media_type == MediaTypeEnum.SHA:
            area_pct = (panel.width * panel.height) / (layout.width * layout.height) * 100
            return SlotRoleEnum.ACCENT if area_pct < 10 else SlotRoleEnum.ICON

        if panel.media_type == MediaTypeEnum.TXT:
            text_len = len(panel.text)
            if panel.font_size >= 28:
                return SlotRoleEnum.TITLE
            if panel.font_size >= 20 or text_len < 50:
                return SlotRoleEnum.SUBTITLE if text_len < 100 else SlotRoleEnum.NUMBER
            if text_len < 30:
                return SlotRoleEnum.CAPTION
            return SlotRoleEnum.BODY

        return SlotRoleEnum.BODY

    def _normalize_coords(self, panel, layout):
        def snap(value):
            return round(value / 5) * 5

        return {
            "left_pct": snap(panel.left / layout.width * 100),
            "top_pct": snap(panel.top / layout.height * 100),
            "width_pct": snap(panel.width / layout.width * 100),
            "height_pct": snap(panel.height / layout.height * 100),
        }

    def _extract_style(self, panel):
        style = {}
        for field_name in STYLE_EXTRACT_FIELDS:
            value = getattr(panel, field_name, None)
            default = PANEL_DEFAULTS.get(field_name)
            if value is not None and value != default:
                style[field_name] = value
        return style

    def _extract_palette(self, page, panels):
        colors = {
            "background": page.background_color,
            "text": "#333333",
            "primary": "#333333",
            "secondary": "#666666",
            "accent": "#0066cc",
        }

        text_colors = [
            p.color for p in panels
            if p.media_type in (MediaTypeEnum.TXT, MediaTypeEnum.HL)
            and p.color != "#ffffff"
        ]
        bg_colors = [
            p.background_color for p in panels
            if p.background_color not in ("transparent", "#ffffff", "#000000")
        ]

        if text_colors:
            colors["text"] = Counter(text_colors).most_common(1)[0][0]

        if bg_colors:
            colors["accent"] = Counter(bg_colors).most_common(1)[0][0]

        title_panels = [p for p in panels if p.media_type == MediaTypeEnum.HL]
        if title_panels:
            colors["primary"] = title_panels[0].color

        return colors

    def _infer_category(self, slots):
        roles = [s["role"] for s in slots]
        has_image = SlotRoleEnum.IMAGE in roles
        has_title = SlotRoleEnum.TITLE in roles
        body_count = roles.count(SlotRoleEnum.BODY)

        if has_title and len(slots) <= 3 and not has_image:
            return PatternCategoryEnum.TITLE
        if has_image and body_count >= 1:
            return PatternCategoryEnum.IMAGE_TEXT
        if has_image:
            return PatternCategoryEnum.IMAGE
        if body_count >= 2:
            return PatternCategoryEnum.CONTENT_TWO_COL
        return PatternCategoryEnum.CONTENT

    def _deduplicate(self, patterns, threshold=0.85):
        unique = []
        for p in patterns:
            is_dup = any(
                self._layout_similarity(p["slots"], u["slots"]) > threshold
                for u in unique
            )
            if not is_dup:
                unique.append(p)
        return unique

    def _layout_similarity(self, slots_a, slots_b):
        if len(slots_a) != len(slots_b):
            return 0.0

        total_sim = 0.0
        for sa in slots_a:
            for sb in slots_b:
                if sa["role"] == sb["role"]:
                    diff = sum(
                        abs(sa[k] - sb[k])
                        for k in ("left_pct", "top_pct", "width_pct", "height_pct")
                    ) / 4
                    total_sim += max(0, 1 - diff / 20)
                    break

        return total_sim / max(len(slots_a), 1)

    def _save_patterns(self, patterns, layout_preset):
        saved = 0
        for p in patterns:
            pattern = DesignPattern.objects.create(
                name=f"Legacy {p['category']} #{saved + 1}",
                category=p["category"],
                target_layout=layout_preset,
                page_background_type=p["page_background_type"],
                page_background_color=p["page_background_color"],
                page_opacity=p["page_opacity"],
                palette=p["palette"],
                source=PatternSourceEnum.LEGACY,
                source_page_id=p["source_page_id"],
            )
            for i, slot_data in enumerate(p["slots"]):
                DesignPatternSlot.objects.create(
                    pattern=pattern,
                    role=slot_data["role"],
                    media_type=slot_data["media_type"],
                    left_pct=slot_data["left_pct"],
                    top_pct=slot_data["top_pct"],
                    width_pct=slot_data["width_pct"],
                    height_pct=slot_data["height_pct"],
                    style=slot_data["style"],
                    order=i,
                )
            saved += 1
        return saved

