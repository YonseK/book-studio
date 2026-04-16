"""PDF 내보내기 서비스.

PubBook의 페이지들을 HTML → PDF로 변환.
WeasyPrint 사용 (선택적 의존성).
"""

import io
from typing import Optional

from bookstudio.services.layout import get_layout
from bookstudio.services.page_renderer import render_page_html


class PDFExportError(Exception):
    pass


def export_pub_book_pdf(pub_book, output=None) -> bytes:
    """PubBook의 전체 페이지를 단일 PDF로 내보내기.

    Args:
        pub_book: PubBook 인스턴스
        output: 파일 객체 (None이면 bytes 반환)

    Returns:
        PDF 바이트 데이터
    """
    try:
        from weasyprint import HTML
    except ImportError:
        raise PDFExportError(
            "weasyprint 패키지가 필요합니다: pip install weasyprint"
        )

    book_layout = pub_book.get_book_layout()
    layout_config = get_layout(book_layout)

    pages_html = []
    for pub_page in pub_book.pages.order_by("order"):
        html = render_page_html(
            pub_page.page,
            width=layout_config.width,
            height=layout_config.height,
            usage="print",
        )
        pages_html.append(html)

    if not pages_html:
        raise PDFExportError("내보낼 페이지가 없습니다.")

    # 페이지를 하나의 HTML 문서로 합치기
    combined_html = _combine_pages_html(pages_html, layout_config)

    html_doc = HTML(string=combined_html)
    pdf_bytes = html_doc.write_pdf()

    if output:
        output.write(pdf_bytes)

    return pdf_bytes


def export_page_pdf(page, output=None) -> bytes:
    """단일 페이지를 PDF로 내보내기."""
    try:
        from weasyprint import HTML
    except ImportError:
        raise PDFExportError(
            "weasyprint 패키지가 필요합니다: pip install weasyprint"
        )

    book = page.book_edition.book if page.book_edition else None
    layout_name = book.book_layout if book else "PPTX_WIDE"
    layout_config = get_layout(layout_name)

    html = render_page_html(
        page,
        width=layout_config.width,
        height=layout_config.height,
        usage="print",
    )

    full_html = _wrap_single_page(html, layout_config)
    html_doc = HTML(string=full_html)
    pdf_bytes = html_doc.write_pdf()

    if output:
        output.write(pdf_bytes)

    return pdf_bytes


def _combine_pages_html(pages_html: list[str], layout_config) -> str:
    """여러 페이지 HTML을 단일 문서로 합치기."""
    w = layout_config.width
    h = layout_config.height
    pw = layout_config.print_width or (w * 0.2646)  # px → mm 근사
    ph = layout_config.print_height or (h * 0.2646)

    pages_content = "\n".join(
        f'<div class="page">{html}</div>' for html in pages_html
    )
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  @page {{
    size: {pw}mm {ph}mm;
    margin: 0;
  }}
  body {{
    margin: 0;
    padding: 0;
  }}
  .page {{
    width: {w}px;
    height: {h}px;
    overflow: hidden;
    position: relative;
    page-break-after: always;
    transform-origin: top left;
    transform: scale({pw * 3.7795 / w});
  }}
  .page:last-child {{
    page-break-after: auto;
  }}
</style>
</head>
<body>
{pages_content}
</body>
</html>"""


def _wrap_single_page(page_html: str, layout_config) -> str:
    """단일 페이지 HTML을 전체 문서로 감싸기."""
    return _combine_pages_html([page_html], layout_config)
