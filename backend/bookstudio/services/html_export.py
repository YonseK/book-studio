"""HTML Export 서비스.

Page/PubPage → 독립 HTML 파일로 내보내기.
에셋 인라인 or 외부 참조 선택.
"""

from bookstudio.models.page import Page
from bookstudio.services.page_renderer import render_page_html
from bookstudio.services.layout import get_layout


def export_page_html(
    page: Page,
    inline_assets: bool = True,
    responsive: bool = False,
) -> str:
    """단일 Page를 독립 HTML 문서로 내보내기.

    Args:
        page: Page 인스턴스
        inline_assets: True이면 에셋을 인라인(base64)으로 포함
        responsive: True이면 뷰포트 기반 반응형 스타일 적용

    Returns:
        완전한 HTML 문서 문자열
    """
    book = page.book_edition.book if page.book_edition else None
    layout_name = book.book_layout if book else "PPTX_WIDE"
    layout_config = get_layout(layout_name)

    page_html = render_page_html(
        page,
        width=layout_config.width,
        height=layout_config.height,
        usage="view",
    )

    width = layout_config.width
    height = layout_config.height

    if responsive:
        viewport_meta = '<meta name="viewport" content="width=device-width, initial-scale=1">'
        responsive_style = f"""
        .bs-page {{
            max-width: 100%;
            height: auto;
            aspect-ratio: {width} / {height};
        }}
        @media (max-width: {width}px) {{
            .bs-page {{
                transform: scale(1) !important;
                width: 100% !important;
                height: auto !important;
            }}
        }}"""
    else:
        viewport_meta = ""
        responsive_style = ""

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
{viewport_meta}
<title>{page.description or "BookStudio Page"}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background: #f0f0f0;
  }}
  {responsive_style}
</style>
</head>
<body>
{page_html}
</body>
</html>"""


def export_book_html(edition, responsive: bool = False) -> list[dict]:
    """BookEdition의 전체 페이지를 HTML 문서 리스트로 내보내기.

    Returns:
        [{"page_id": ..., "order": ..., "html": ...}, ...]
    """
    pages = edition.pages.filter(deleted=False).order_by("order")
    result = []

    for page in pages:
        html = export_page_html(page, responsive=responsive)
        result.append({
            "page_id": page.id,
            "order": page.order,
            "short_key": page.short_key,
            "html": html,
        })

    return result
