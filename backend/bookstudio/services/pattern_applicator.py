"""DesignPattern → Page + Panels 변환 서비스."""

from dataclasses import dataclass, field

from bookstudio.models import Page, Panel, Document
from bookstudio.models.design_pattern import DesignPattern
from bookstudio.services.layout import LayoutConfig


@dataclass
class SlotContent:
    """AI가 생성한 슬롯별 콘텐츠."""

    role: str
    text: str = ""
    headline: str = ""
    image_id: str | None = None
    document_html: str | None = None
    fields_data: dict | None = None  # 확장 속성 (icon_class, badge_text 등)


@dataclass
class PatternApplyResult:
    page: Page
    panels: list[Panel] = field(default_factory=list)
    document: Document | None = None


class PatternApplicator:
    """DesignPattern → Page + Panels 변환."""

    ALLOWED_STYLE_KEYS = frozenset({
        "font_size", "font_family", "font_weight", "font_style",
        "font_bold", "font_italic", "color", "text_align",
        "letter_spacing", "line_height", "text_decoration",
        "background_color", "background_opacity", "padding",
        "border_width", "border_radius", "border_color",
        "border_style", "border_opacity",
        "box_shadow", "box_shadow_px", "text_shadow", "text_shadow_px",
        "opacity", "rotate", "shape_type", "stroke_width",
    })

    _ROLE_PALETTE_MAP = {
        "title": "text",
        "subtitle": "secondary",
        "body": "text",
        "number": "accent",
        "caption": "text",
        "icon": "primary",
        "stat_value": "text",
        "stat_label": "secondary",
        "badge": "accent",
        "icon_box": "primary",
        "header": "text",
        "footer": "muted",
        "summary": "text",
        "flow_node": "text",
        "chart_area": "text",
        "progress": "primary",
    }

    def apply(
        self,
        pattern: DesignPattern,
        layout: LayoutConfig,
        contents: list[SlotContent],
        edition_id: str,
        user_id: str,
        page_order: int,
        palette_override: dict | None = None,
    ) -> PatternApplyResult:
        palette = palette_override or pattern.palette or {}
        typography = pattern.typography or {}

        # Page 생성
        page = Page.objects.create(
            book_edition_id=edition_id,
            user_id=user_id,
            background_type=pattern.page_background_type,
            background_color=palette.get("background", pattern.page_background_color),
            opacity=pattern.page_opacity,
            order=page_order,
        )

        # 콘텐츠를 role로 인덱싱
        content_map: dict[str, SlotContent] = {}
        for c in contents:
            content_map.setdefault(c.role, c)

        # Slot → Panel 변환
        panels = []
        for slot in pattern.slots.order_by("order"):
            content = content_map.get(slot.role, SlotContent(role=slot.role))
            panel = self._create_panel(
                slot=slot,
                content=content,
                page=page,
                layout=layout,
                user_id=user_id,
                palette=palette,
                typography=typography,
                panel_order=slot.order,
            )
            panels.append(panel)

        # Document 생성
        document = None
        body_content = content_map.get("body")
        if body_content and body_content.document_html:
            document = Document.objects.create(
                page=page,
                user_id=user_id,
                contents=body_content.document_html,
                edit_type="WYSIWYG",
            )

        pattern.increment_usage()

        return PatternApplyResult(page=page, panels=panels, document=document)

    def _create_panel(
        self, slot, content, page, layout, user_id, palette, typography, panel_order
    ) -> Panel:
        coords = slot.to_absolute(layout.width, layout.height)

        # slot.style에서 허용 키만 추출
        style_kwargs = {
            k: v for k, v in (slot.style or {}).items()
            if k in self.ALLOWED_STYLE_KEYS
        }

        # 팔레트 기반 색상 자동 적용
        if "color" not in style_kwargs:
            palette_key = self._ROLE_PALETTE_MAP.get(slot.role, "text")
            style_kwargs["color"] = palette.get(palette_key, "#333333")

        # 타이포그래피 자동 적용
        if "font_family" not in style_kwargs and typography:
            if slot.role in ("title", "subtitle", "number"):
                style_kwargs.setdefault(
                    "font_family", typography.get("heading_font", "initial")
                )
            else:
                style_kwargs.setdefault(
                    "font_family", typography.get("body_font", "initial")
                )

        if "font_size" not in style_kwargs and typography:
            heading_size = typography.get("heading_size", 32)
            if slot.role == "title":
                style_kwargs.setdefault("font_size", heading_size)
            elif slot.role == "subtitle":
                style_kwargs.setdefault("font_size", max(heading_size - 8, 16))

        # fields_data: slot.style 중 ALLOWED 외 키 + content.fields_data 병합
        fields_data = {
            k: v for k, v in (slot.style or {}).items()
            if k not in self.ALLOWED_STYLE_KEYS
        }
        if content.fields_data:
            fields_data.update(content.fields_data)

        return Panel.objects.create(
            page=page,
            user_id=user_id,
            media_type=slot.media_type,
            text=content.text,
            headline=content.headline,
            image_id=content.image_id,
            order=panel_order,
            fields_data=fields_data or None,
            **coords,
            **style_kwargs,
        )
