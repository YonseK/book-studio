"""페이지 HTML 렌더러.

Page 모델 → HTML 문자열 변환.
원본 adapter.py의 rendered_page_html 로직을 서비스로 추출.
PDF 내보내기, HTML Export, 페이지 썸네일 생성에 공통 사용.
"""

from bookstudio.models.page import Page
from bookstudio.models.panel import Panel, MediaTypeEnum


def render_page_html(
    page: Page,
    width: int = 1280,
    height: int = 720,
    usage: str = "view",
    scale_x: float = 1.0,
    scale_y: float = 1.0,
) -> str:
    """Page를 HTML 문자열로 렌더링.

    Args:
        page: Page 인스턴스
        width: 캔버스 너비 (px)
        height: 캔버스 높이 (px)
        usage: "view" | "print" | "thumbnail"
        scale_x/scale_y: 스케일 팩터

    Returns:
        HTML 문자열
    """
    bg_style = _build_background_style(page)
    panels_html = _render_panels(page, usage)

    return f"""<div class="bs-page" style="
        position: relative;
        width: {width}px;
        height: {height}px;
        overflow: hidden;
        {bg_style}
        transform: scale({scale_x}, {scale_y});
        transform-origin: top left;
    ">
{panels_html}
</div>"""


def _build_background_style(page: Page) -> str:
    """페이지 배경 CSS 생성."""
    bg_type = page.background_type

    if bg_type == "WP":
        # 월페이퍼 배경
        wp = page.wallpaper
        wp_img = page.wallpaper_image
        url = ""
        if wp and wp.image:
            url = wp.image.url
        elif wp_img and wp_img.image:
            url = wp_img.image.url

        if url:
            pos_x = page.background_position_x
            pos_y = page.background_position_y
            return (
                f"background-image: url('{url}');"
                f"background-size: cover;"
                f"background-position: {pos_x}% {pos_y}%;"
                f"opacity: {page.opacity};"
            )

    # 기본: 컬러 배경
    return f"background-color: {page.background_color}; opacity: {page.opacity};"


def _render_panels(page: Page, usage: str) -> str:
    """페이지 내 패널들을 HTML로 렌더링."""
    panels = page.panels.filter(deleted=False, is_active=True).order_by("order")
    parts = []

    for panel in panels:
        html = _render_panel(panel, usage)
        parts.append(html)

    return "\n".join(parts)


def _render_panel(panel: Panel, usage: str) -> str:
    """단일 패널 → HTML."""
    style = _build_panel_style(panel)
    content = _build_panel_content(panel, usage)

    return f"""<div class="bs-panel bs-panel-{panel.media_type.lower()}"
     data-panel-id="{panel.id}"
     style="{style}">
{content}
</div>"""


def _build_panel_style(panel: Panel) -> str:
    """패널 CSS 인라인 스타일 생성."""
    parts = [
        "position: absolute;",
        f"left: {panel.left}px;",
        f"top: {panel.top}px;",
        f"width: {panel.width}px;",
        f"height: {panel.height}px;",
        f"z-index: {panel.z_index};",
        f"opacity: {panel.opacity};",
        f"padding: {panel.padding}px;",
        f"background-color: {panel.background_color};",
    ]

    if panel.rotate:
        parts.append(f"transform: rotate({panel.rotate}deg);")

    if panel.border_width:
        parts.append(
            f"border: {panel.border_width}px {panel.border_style} {panel.border_color};"
        )

    if panel.border_radius:
        parts.append(f"border-radius: {panel.border_radius}px;")

    if panel.box_shadow != "initial":
        parts.append(f"box-shadow: {panel.box_shadow};")

    return " ".join(parts)


def _build_panel_content(panel: Panel, usage: str) -> str:
    """패널 타입별 콘텐츠 HTML."""
    mt = panel.media_type

    if mt in (MediaTypeEnum.TXT, MediaTypeEnum.DOC):
        style = _text_style(panel)
        return f'<div class="bs-text" style="{style}">{panel.text}</div>'

    if mt == MediaTypeEnum.HL:
        style = _text_style(panel)
        return f'<div class="bs-headline" style="{style}">{panel.headline}</div>'

    if mt == MediaTypeEnum.IMG:
        img_url = ""
        if panel.image and panel.image.image:
            img_url = panel.image.image.url if usage == "print" else panel.image.get_image_view_url()
        mask_class = f"bs-mask-{panel.masked_image.lower()}" if panel.masked_image else ""
        return (
            f'<img class="bs-image {mask_class}" '
            f'src="{img_url}" '
            f'style="width: 100%; height: 100%; object-fit: cover;" />'
        )

    if mt == MediaTypeEnum.SHA:
        return f'<div class="bs-shape" data-shape-type="{panel.shape_type}"></div>'

    if mt == MediaTypeEnum.VOD:
        return '<div class="bs-video">[Video]</div>'

    if mt == MediaTypeEnum.EV:
        return '<div class="bs-embed">[Embed]</div>'

    if mt == MediaTypeEnum.WS:
        url = panel.link_url or ""
        return f'<div class="bs-webscraping" data-url="{url}">[Web Scraping]</div>'

    if mt == MediaTypeEnum.PDF:
        return '<div class="bs-pdf">[PDF]</div>'

    if mt == MediaTypeEnum.FILE:
        return '<div class="bs-file">[File]</div>'

    if mt == MediaTypeEnum.WGT:
        return '<div class="bs-widget">[Widget]</div>'

    return f'<div class="bs-unknown">{panel.text}</div>'


def _text_style(panel: Panel) -> str:
    """텍스트 관련 CSS."""
    parts = [
        f"font-size: {panel.font_size}px;",
        f"font-family: {panel.font_family};",
        f"color: {panel.color};",
        f"text-align: {panel.text_align};",
        f"letter-spacing: {panel.letter_spacing}px;",
        f"line-height: {panel.line_height};",
    ]
    if panel.font_bold:
        parts.append("font-weight: bold;")
    if panel.font_italic:
        parts.append("font-style: italic;")
    if panel.text_underline:
        parts.append("text-decoration: underline;")
    if panel.text_shadow != "initial":
        parts.append(f"text-shadow: {panel.text_shadow};")
    return " ".join(parts)
