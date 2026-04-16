"""Phase 2 나머지(2-4~2-6) 테스트.

- page_renderer: 페이지 HTML 렌더링
- html_import: 외부 HTML → Page/Panel 변환
- html_export: Page → 독립 HTML 내보내기
- pdf_export: PDF 변환 (weasyprint 없을 때 에러 처리)
- consumers: WebSocket placeholder
- API 엔드포인트
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from bookstudio.models import (
    Book,
    BookEdition,
    BookLayoutEnum,
    Page,
    Panel,
    MediaTypeEnum,
    PubBook,
    PubPage,
)
from bookstudio.services.page_renderer import render_page_html, _build_panel_style
from bookstudio.services.html_import import (
    sanitize_html,
    import_html,
    HTMLImportError,
    _SectionSplitter,
    _ElementExtractor,
)
from bookstudio.services.html_export import export_page_html, export_book_html

User = get_user_model()
BASE = "/api/studio"


@pytest.fixture
def user(db):
    return User.objects.create_user(username="phase2user", password="pass")


@pytest.fixture
def client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.fixture
def book(user):
    return Book.objects.create(user=user, book_layout=BookLayoutEnum.PPTX_WIDE)


@pytest.fixture
def edition(book):
    return BookEdition.objects.create(book=book, title="Test", version=1, latest=True)


@pytest.fixture
def page_with_panels(user, edition):
    page = Page.objects.create(
        user=user,
        book_edition=edition,
        order=0,
        background_color="#f0f0f0",
    )
    Panel.objects.create(
        user=user,
        page=page,
        media_type=MediaTypeEnum.HL,
        order=0,
        headline="제목입니다",
        left=40,
        top=20,
        width=600,
        height=60,
        font_size=32,
        font_bold=True,
    )
    Panel.objects.create(
        user=user,
        page=page,
        media_type=MediaTypeEnum.TXT,
        order=1,
        text="본문 텍스트입니다.",
        left=40,
        top=100,
        width=600,
        height=200,
    )
    Panel.objects.create(
        user=user,
        page=page,
        media_type=MediaTypeEnum.IMG,
        order=2,
        left=40,
        top=320,
        width=400,
        height=300,
    )
    return page


# ──────────────────── page_renderer ────────────────────


class TestPageRenderer:
    def test_render_basic(self, page_with_panels):
        html = render_page_html(page_with_panels, width=1280, height=720)
        assert 'class="bs-page"' in html
        assert "1280px" in html
        assert "720px" in html

    def test_render_contains_panels(self, page_with_panels):
        html = render_page_html(page_with_panels)
        assert "제목입니다" in html
        assert "본문 텍스트입니다" in html
        assert "bs-panel-img" in html

    def test_render_background_color(self, page_with_panels):
        html = render_page_html(page_with_panels)
        assert "#f0f0f0" in html

    def test_render_headline_style(self, page_with_panels):
        html = render_page_html(page_with_panels)
        assert "font-weight: bold" in html

    def test_build_panel_style(self, page_with_panels):
        panel = page_with_panels.panels.first()
        style = _build_panel_style(panel)
        assert "left: 40px" in style
        assert "z-index:" in style


# ──────────────────── html_import ────────────────────


class TestSanitizeHtml:
    def test_removes_script(self):
        result = sanitize_html('<p>hello</p><script>alert("xss")</script>')
        assert "<script>" not in result
        assert "hello" in result

    def test_removes_style_tag(self):
        result = sanitize_html("<style>body{color:red}</style><p>ok</p>")
        assert "<style>" not in result

    def test_removes_event_handlers(self):
        result = sanitize_html('<div onclick="alert(1)">click</div>')
        assert "onclick" not in result

    def test_preserves_safe_html(self):
        html = "<h1>Title</h1><p>Paragraph</p><img src='test.jpg'>"
        result = sanitize_html(html)
        assert "<h1>" in result
        assert "<p>" in result
        assert "<img" in result


class TestSectionSplitter:
    def test_splits_on_section(self):
        html = "<p>first</p><section><p>second</p></section><p>third</p>"
        splitter = _SectionSplitter()
        splitter.feed(html)
        sections = splitter.get_sections()
        assert len(sections) >= 2

    def test_splits_on_hr(self):
        html = "<p>part1</p><hr><p>part2</p>"
        splitter = _SectionSplitter()
        splitter.feed(html)
        sections = splitter.get_sections()
        assert len(sections) == 2

    def test_single_section(self):
        html = "<p>only one</p>"
        splitter = _SectionSplitter()
        splitter.feed(html)
        sections = splitter.get_sections()
        assert len(sections) == 1


class TestElementExtractor:
    def test_extracts_heading(self):
        extractor = _ElementExtractor()
        extractor.feed("<h1>Title</h1>")
        panels = extractor.get_panels()
        assert len(panels) == 1
        assert panels[0]["media_type"] == MediaTypeEnum.HL
        assert panels[0]["headline"] == "Title"
        assert panels[0]["font_size"] == 32

    def test_extracts_paragraph(self):
        extractor = _ElementExtractor()
        extractor.feed("<p>Hello world</p>")
        panels = extractor.get_panels()
        assert len(panels) == 1
        assert panels[0]["media_type"] == MediaTypeEnum.TXT
        assert panels[0]["text"] == "Hello world"

    def test_extracts_image(self):
        extractor = _ElementExtractor()
        extractor.feed('<img src="test.jpg" width="800" height="600">')
        panels = extractor.get_panels()
        assert len(panels) == 1
        assert panels[0]["media_type"] == MediaTypeEnum.IMG
        assert panels[0]["width"] == 800

    def test_mixed_content(self):
        html = "<h2>Heading</h2><p>Text</p><img src='a.jpg'>"
        extractor = _ElementExtractor()
        extractor.feed(html)
        panels = extractor.get_panels()
        assert len(panels) == 3


class TestImportHtml:
    def test_basic_import(self, user, edition):
        html = "<h1>Slide 1</h1><p>Content here</p>"
        pages = import_html(html, edition, user)
        assert len(pages) == 1
        page = pages[0]
        assert page.panels.count() == 2

    def test_multi_section_import(self, user, edition):
        html = "<section><h1>Page 1</h1></section><section><h2>Page 2</h2></section>"
        pages = import_html(html, edition, user)
        assert len(pages) == 2

    def test_empty_html_raises(self, user, edition):
        with pytest.raises(HTMLImportError):
            import_html("", edition, user)

    def test_order_continues(self, user, edition):
        Page.objects.create(user=user, book_edition=edition, order=0)
        pages = import_html("<p>new</p>", edition, user)
        assert pages[0].order == 1

    def test_panels_have_position(self, user, edition):
        pages = import_html("<h1>Title</h1><p>Body</p>", edition, user)
        panels = list(pages[0].panels.order_by("order"))
        assert panels[0].top == 20
        assert panels[1].top > panels[0].top


# ──────────────────── html_export ────────────────────


class TestHtmlExport:
    def test_export_page(self, page_with_panels):
        html = export_page_html(page_with_panels)
        assert "<!DOCTYPE html>" in html
        assert "제목입니다" in html
        assert "본문 텍스트입니다" in html

    def test_export_responsive(self, page_with_panels):
        html = export_page_html(page_with_panels, responsive=True)
        assert "viewport" in html
        assert "aspect-ratio" in html

    def test_export_book(self, user, edition, page_with_panels):
        result = export_book_html(edition)
        assert len(result) == 1
        assert result[0]["page_id"] == page_with_panels.id
        assert "<!DOCTYPE html>" in result[0]["html"]


# ──────────────────── pdf_export (weasyprint 선택적) ────────────────────


class TestPdfExport:
    def test_import_error_message(self):
        """weasyprint 미설치 시 친절한 에러 메시지."""
        from bookstudio.services.pdf_export import PDFExportError
        # 이 테스트 환경에서는 weasyprint이 없으므로 에러 발생 확인
        try:
            from weasyprint import HTML
            has_weasyprint = True
        except ImportError:
            has_weasyprint = False

        if not has_weasyprint:
            from bookstudio.services.pdf_export import export_page_pdf
            with pytest.raises(PDFExportError, match="weasyprint"):
                export_page_pdf(Page())


# ──────────────────── WebSocket Consumer ────────────────────


class TestWebSocketConsumer:
    def test_consumer_exists(self):
        from bookstudio.consumers import BookStudioConsumer
        assert BookStudioConsumer is not None

    def test_channels_not_required(self):
        """channels 미설치 시 placeholder 동작."""
        try:
            import channels
            has_channels = True
        except ImportError:
            has_channels = False

        if not has_channels:
            from bookstudio.consumers import BookStudioConsumer
            with pytest.raises(ImportError, match="channels"):
                BookStudioConsumer()


# ──────────────────── API 엔드포인트 ────────────────────


class TestHtmlImportAPI:
    def test_import_endpoint(self, client, user, edition):
        resp = client.post(
            f"{BASE}/import/html/",
            {
                "html": "<h1>슬라이드</h1><p>내용</p>",
                "edition_id": edition.pk,
            },
            format="json",
        )
        assert resp.status_code == 201
        assert resp.data["pages"]
        assert len(resp.data["pages"]) == 1

    def test_import_empty_html(self, client, edition):
        resp = client.post(
            f"{BASE}/import/html/",
            {"html": "", "edition_id": edition.pk},
            format="json",
        )
        assert resp.status_code == 400

    def test_import_invalid_edition(self, client):
        resp = client.post(
            f"{BASE}/import/html/",
            {"html": "<p>test</p>", "edition_id": "nonexistent"},
            format="json",
        )
        assert resp.status_code == 404


class TestHtmlExportAPI:
    def test_export_page_endpoint(self, client, page_with_panels):
        resp = client.get(
            f"{BASE}/export/html/page/{page_with_panels.pk}/"
        )
        assert resp.status_code == 200
        assert "<!DOCTYPE html>" in resp.data["html"]

    def test_export_book_endpoint(self, client, edition, page_with_panels):
        resp = client.get(
            f"{BASE}/export/html/edition/{edition.pk}/"
        )
        assert resp.status_code == 200
        assert len(resp.data["pages"]) == 1

    def test_export_nonexistent_page(self, client):
        resp = client.get(f"{BASE}/export/html/page/nonexistent/")
        assert resp.status_code == 404
