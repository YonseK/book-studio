"""HTML Import 서비스.

외부 HTML → BookStudio Page/Panel 구조로 변환.
설계 문서 4.4절 전략:
1. 안전하지 않은 태그/스크립트 제거
2. DOM 구조 분석
3. 블록 요소 → Page 분할
4. 인라인/텍스트 → TextPanel
5. img → ImagePanel
6. iframe/embed → EmbedPanel
7. CSS → 패널 속성으로 변환
"""

import re
from html.parser import HTMLParser
from typing import Optional

from bookstudio.models.page import Page
from bookstudio.models.panel import Panel, MediaTypeEnum
from bookstudio.models.book import BookEdition


class HTMLImportError(Exception):
    pass


# 제거할 태그
DISALLOWED_TAGS = {"script", "style", "link", "meta", "noscript", "iframe", "object", "embed", "form", "input"}
# 페이지 분할 기준 태그
PAGE_BREAK_TAGS = {"section", "article", "hr"}
# 블록 요소
BLOCK_TAGS = {"div", "p", "h1", "h2", "h3", "h4", "h5", "h6", "blockquote", "pre", "ul", "ol", "li", "table", "figure"}


def sanitize_html(html_string: str) -> str:
    """안전하지 않은 태그 제거."""
    for tag in DISALLOWED_TAGS:
        html_string = re.sub(
            rf"<{tag}[^>]*>.*?</{tag}>",
            "",
            html_string,
            flags=re.DOTALL | re.IGNORECASE,
        )
        html_string = re.sub(
            rf"<{tag}[^>]*/?>",
            "",
            html_string,
            flags=re.IGNORECASE,
        )
    # on* 이벤트 핸들러 제거
    html_string = re.sub(r'\s+on\w+="[^"]*"', "", html_string, flags=re.IGNORECASE)
    html_string = re.sub(r"\s+on\w+='[^']*'", "", html_string, flags=re.IGNORECASE)
    return html_string


class _SectionSplitter(HTMLParser):
    """HTML을 섹션 단위로 분할하는 파서."""

    def __init__(self):
        super().__init__()
        self.sections: list[str] = []
        self._current: list[str] = []
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in PAGE_BREAK_TAGS and self._current:
            self.sections.append("".join(self._current))
            self._current = []
        attrs_str = " ".join(f'{k}="{v}"' for k, v in attrs) if attrs else ""
        self._current.append(f"<{tag} {attrs_str}>" if attrs_str else f"<{tag}>")

    def handle_endtag(self, tag):
        self._current.append(f"</{tag}>")

    def handle_data(self, data):
        self._current.append(data)

    def get_sections(self) -> list[str]:
        if self._current:
            self.sections.append("".join(self._current))
        return [s.strip() for s in self.sections if s.strip()]


class _ElementExtractor(HTMLParser):
    """섹션 내 요소를 Panel 데이터로 추출하는 파서."""

    def __init__(self):
        super().__init__()
        self.panels: list[dict] = []
        self._text_buffer: list[str] = []
        self._in_heading = False
        self._heading_tag = ""

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs) if attrs else {}

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self._flush_text()
            self._in_heading = True
            self._heading_tag = tag

        elif tag == "img":
            self._flush_text()
            src = attrs_dict.get("src", "")
            self.panels.append({
                "media_type": MediaTypeEnum.IMG,
                "link_url": src,
                "width": _parse_dim(attrs_dict.get("width"), 400),
                "height": _parse_dim(attrs_dict.get("height"), 300),
            })

        elif tag == "video":
            self._flush_text()
            self.panels.append({"media_type": MediaTypeEnum.VOD})

        elif tag == "a":
            href = attrs_dict.get("href", "")
            if href:
                self._text_buffer.append(f'<a href="{href}">')

    def handle_endtag(self, tag):
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self._in_heading:
            text = "".join(self._text_buffer).strip()
            if text:
                font_size = {"h1": 32, "h2": 28, "h3": 24, "h4": 20, "h5": 18, "h6": 16}.get(
                    self._heading_tag, 16
                )
                self.panels.append({
                    "media_type": MediaTypeEnum.HL,
                    "headline": text,
                    "font_size": font_size,
                    "font_bold": True,
                })
            self._text_buffer = []
            self._in_heading = False

        elif tag == "a":
            self._text_buffer.append("</a>")

        elif tag in ("p", "div", "blockquote", "li"):
            self._flush_text()

    def handle_data(self, data):
        stripped = data.strip()
        if stripped:
            self._text_buffer.append(stripped)

    def _flush_text(self):
        text = " ".join(self._text_buffer).strip()
        if text:
            self.panels.append({
                "media_type": MediaTypeEnum.TXT,
                "text": text,
            })
        self._text_buffer = []

    def get_panels(self) -> list[dict]:
        self._flush_text()
        return self.panels


def _parse_dim(value: Optional[str], default: int) -> int:
    """문자열 치수를 정수로 변환."""
    if not value:
        return default
    try:
        return int(re.sub(r"[^\d]", "", value))
    except (ValueError, TypeError):
        return default


def import_html(
    html_string: str,
    edition: BookEdition,
    user,
    page_width: int = 1280,
    page_height: int = 720,
) -> list[Page]:
    """HTML 문자열을 BookEdition에 Page/Panel로 변환.

    Args:
        html_string: 외부 HTML 소스
        edition: 대상 BookEdition
        user: 작업 수행 사용자
        page_width/height: 페이지 캔버스 크기

    Returns:
        생성된 Page 리스트
    """
    cleaned = sanitize_html(html_string)

    # 섹션 분할
    splitter = _SectionSplitter()
    splitter.feed(cleaned)
    sections = splitter.get_sections()

    if not sections:
        raise HTMLImportError("변환 가능한 콘텐츠가 없습니다.")

    # 기존 페이지 수
    last_order = edition.pages.order_by("-order").values_list("order", flat=True).first()
    next_order = (last_order + 1) if last_order is not None else 0

    created_pages = []

    for i, section_html in enumerate(sections):
        # 요소 추출
        extractor = _ElementExtractor()
        extractor.feed(section_html)
        panel_data_list = extractor.get_panels()

        if not panel_data_list:
            continue

        page = Page.objects.create(
            user=user,
            book_edition=edition,
            order=next_order + i,
            description=f"Imported page {i + 1}",
        )

        # 패널 배치 (세로 자동 레이아웃)
        y_cursor = 20
        for j, pdata in enumerate(panel_data_list):
            media_type = pdata.pop("media_type")
            panel_kwargs = {
                "user": user,
                "page": page,
                "media_type": media_type,
                "order": j,
                "left": 40,
                "top": y_cursor,
                "width": pdata.pop("width", page_width - 80),
                "height": pdata.pop("height", 60 if media_type in (MediaTypeEnum.TXT, MediaTypeEnum.HL) else 300),
            }
            panel_kwargs.update(pdata)
            Panel.objects.create(**panel_kwargs)
            y_cursor += panel_kwargs["height"] + 10

        created_pages.append(page)

    return created_pages
