"""디자인 패턴 모델, 서비스, API 테스트."""

import pytest
from django.contrib.auth import get_user_model

from bookstudio.models import Book, BookEdition, Page, Panel
from bookstudio.models.design_pattern import (
    DesignPattern,
    DesignPatternSlot,
    DesignPatternSet,
    DesignPatternSetMembership,
    PatternCategoryEnum,
    SlotRoleEnum,
    PatternSourceEnum,
)
from bookstudio.services.pattern_applicator import (
    PatternApplicator,
    SlotContent,
)
from bookstudio.services.layout import get_layout

User = get_user_model()


# ── Fixtures ──


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="testpass")


@pytest.fixture
def book(user):
    return Book.objects.create(user=user, book_mode="BOOK", book_layout="PPTX_WIDE")


@pytest.fixture
def edition(book):
    return BookEdition.objects.create(book=book, title="Test Edition", latest=True)


@pytest.fixture
def pattern(db):
    return DesignPattern.objects.create(
        name="Test Title Pattern",
        category=PatternCategoryEnum.TITLE,
        target_layout="PPTX_WIDE",
        page_background_color="#1a1a2e",
        palette={
            "primary": "#e94560",
            "secondary": "#533483",
            "accent": "#e94560",
            "text": "#ffffff",
            "background": "#1a1a2e",
        },
        typography={
            "heading_font": "Pretendard",
            "body_font": "Pretendard",
            "heading_size": 48,
            "body_size": 18,
        },
    )


@pytest.fixture
def pattern_with_slots(pattern):
    DesignPatternSlot.objects.create(
        pattern=pattern,
        role=SlotRoleEnum.TITLE,
        media_type="HL",
        left_pct=10, top_pct=30, width_pct=80, height_pct=20,
        style={"font_size": 48, "font_bold": True, "text_align": "center"},
        order=0,
    )
    DesignPatternSlot.objects.create(
        pattern=pattern,
        role=SlotRoleEnum.SUBTITLE,
        media_type="TXT",
        left_pct=20, top_pct=55, width_pct=60, height_pct=10,
        style={"font_size": 20, "text_align": "center"},
        order=1,
    )
    return pattern


@pytest.fixture
def pattern_set(pattern_with_slots):
    ps = DesignPatternSet.objects.create(
        name="Test Set",
        palette={
            "primary": "#ff0000",
            "secondary": "#00ff00",
            "accent": "#0000ff",
            "text": "#ffffff",
            "background": "#000000",
        },
        target_layout="PPTX_WIDE",
    )
    DesignPatternSetMembership.objects.create(
        pattern_set=ps, pattern=pattern_with_slots, priority=0
    )
    return ps


# ── Model Tests ──


class TestDesignPattern:
    def test_create_pattern(self, pattern):
        assert pattern.name == "Test Title Pattern"
        assert pattern.category == PatternCategoryEnum.TITLE
        assert pattern.is_active is True
        assert pattern.usage_count == 0

    def test_increment_usage(self, pattern):
        pattern.increment_usage()
        pattern.refresh_from_db()
        assert pattern.usage_count == 1

        pattern.increment_usage()
        pattern.refresh_from_db()
        assert pattern.usage_count == 2


class TestDesignPatternSlot:
    def test_to_absolute_pptx_wide(self, pattern_with_slots):
        slot = pattern_with_slots.slots.first()
        coords = slot.to_absolute(1280, 720)
        assert coords == {"left": 128, "top": 216, "width": 1024, "height": 144}

    def test_to_absolute_book(self, pattern_with_slots):
        slot = pattern_with_slots.slots.first()
        coords = slot.to_absolute(768, 1086)
        assert coords == {"left": 77, "top": 326, "width": 614, "height": 217}


class TestDesignPatternSet:
    def test_get_pattern_by_category(self, pattern_set, pattern_with_slots):
        result = pattern_set.get_pattern(PatternCategoryEnum.TITLE)
        assert result == pattern_with_slots

    def test_get_pattern_missing_category(self, pattern_set):
        result = pattern_set.get_pattern(PatternCategoryEnum.CLOSING)
        assert result is None

    def test_get_patterns_by_category(self, pattern_set, pattern_with_slots):
        by_cat = pattern_set.get_patterns_by_category()
        assert PatternCategoryEnum.TITLE in by_cat
        assert pattern_with_slots in by_cat[PatternCategoryEnum.TITLE]


# ── Service Tests ──


class TestPatternApplicator:
    def test_apply_creates_page_and_panels(self, pattern_with_slots, edition, user):
        applicator = PatternApplicator()
        layout = get_layout("PPTX_WIDE")
        contents = [
            SlotContent(role="title", headline="Hello World"),
            SlotContent(role="subtitle", text="Subtitle text"),
        ]

        result = applicator.apply(
            pattern=pattern_with_slots,
            layout=layout,
            contents=contents,
            edition_id=str(edition.id),
            user_id=str(user.id),
            page_order=0,
        )

        assert result.page is not None
        assert len(result.panels) == 2
        assert result.page.background_color == "#1a1a2e"

    def test_apply_coordinates_match_layout(self, pattern_with_slots, edition, user):
        applicator = PatternApplicator()
        layout = get_layout("PPTX_WIDE")
        contents = [
            SlotContent(role="title", headline="Test"),
            SlotContent(role="subtitle", text="Sub"),
        ]

        result = applicator.apply(
            pattern=pattern_with_slots,
            layout=layout,
            contents=contents,
            edition_id=str(edition.id),
            user_id=str(user.id),
            page_order=0,
        )

        title_panel = result.panels[0]
        # left_pct=10 of 1280 = 128
        assert title_panel.left == 128
        # width_pct=80 of 1280 = 1024
        assert title_panel.width == 1024

    def test_apply_palette_color_mapping(self, pattern_with_slots, edition, user):
        applicator = PatternApplicator()
        layout = get_layout("PPTX_WIDE")
        contents = [
            SlotContent(role="title", headline="Test"),
            SlotContent(role="subtitle", text="Sub"),
        ]

        result = applicator.apply(
            pattern=pattern_with_slots,
            layout=layout,
            contents=contents,
            edition_id=str(edition.id),
            user_id=str(user.id),
            page_order=0,
        )

        # subtitle의 style에 color 없음 → palette["secondary"] = "#533483"
        subtitle_panel = result.panels[1]
        assert subtitle_panel.color == "#533483"

    def test_apply_with_palette_override(self, pattern_with_slots, edition, user):
        applicator = PatternApplicator()
        layout = get_layout("PPTX_WIDE")
        contents = [
            SlotContent(role="title", headline="Test"),
            SlotContent(role="subtitle", text="Sub"),
        ]

        override = {
            "primary": "#ff0000",
            "secondary": "#00ff00",
            "accent": "#0000ff",
            "text": "#ffffff",
            "background": "#111111",
        }

        result = applicator.apply(
            pattern=pattern_with_slots,
            layout=layout,
            contents=contents,
            edition_id=str(edition.id),
            user_id=str(user.id),
            page_order=0,
            palette_override=override,
        )

        assert result.page.background_color == "#111111"
        # subtitle → secondary → "#00ff00"
        assert result.panels[1].color == "#00ff00"

    def test_apply_with_document(self, pattern_with_slots, edition, user):
        applicator = PatternApplicator()
        layout = get_layout("PPTX_WIDE")
        contents = [
            SlotContent(role="title", headline="Test"),
            SlotContent(role="body", text="Body", document_html="<p>HTML content</p>"),
        ]

        result = applicator.apply(
            pattern=pattern_with_slots,
            layout=layout,
            contents=contents,
            edition_id=str(edition.id),
            user_id=str(user.id),
            page_order=0,
        )

        assert result.document is not None
        assert result.document.contents == "<p>HTML content</p>"

    def test_apply_without_document(self, pattern_with_slots, edition, user):
        applicator = PatternApplicator()
        layout = get_layout("PPTX_WIDE")
        contents = [
            SlotContent(role="title", headline="Test"),
        ]

        result = applicator.apply(
            pattern=pattern_with_slots,
            layout=layout,
            contents=contents,
            edition_id=str(edition.id),
            user_id=str(user.id),
            page_order=0,
        )

        assert result.document is None

    def test_apply_increments_usage(self, pattern_with_slots, edition, user):
        applicator = PatternApplicator()
        layout = get_layout("PPTX_WIDE")

        applicator.apply(
            pattern=pattern_with_slots,
            layout=layout,
            contents=[],
            edition_id=str(edition.id),
            user_id=str(user.id),
            page_order=0,
        )

        pattern_with_slots.refresh_from_db()
        assert pattern_with_slots.usage_count == 1

    def test_style_allowlist(self, edition, user, db):
        """허용되지 않은 스타일 키는 무시."""
        pattern = DesignPattern.objects.create(
            name="Dangerous",
            category=PatternCategoryEnum.CONTENT,
        )
        DesignPatternSlot.objects.create(
            pattern=pattern,
            role=SlotRoleEnum.BODY,
            media_type="TXT",
            left_pct=0, top_pct=0, width_pct=100, height_pct=100,
            style={"font_size": 20, "INVALID_KEY": "bad_value"},
            order=0,
        )

        applicator = PatternApplicator()
        layout = get_layout("PPTX_WIDE")
        result = applicator.apply(
            pattern=pattern,
            layout=layout,
            contents=[SlotContent(role="body", text="Test")],
            edition_id=str(edition.id),
            user_id=str(user.id),
            page_order=0,
        )

        panel = result.panels[0]
        assert panel.font_size == 20
        assert not hasattr(panel, "INVALID_KEY")


# ── Fixture Load Test ──


@pytest.mark.django_db
class TestCuratedPatterns:
    @pytest.fixture(autouse=True)
    def load_fixtures(self):
        from django.core.management import call_command
        call_command("loaddata", "curated_patterns", verbosity=0)

    def test_fixture_loads_15_patterns(self):
        assert DesignPattern.objects.count() == 15

    def test_fixture_loads_pattern_set(self):
        assert DesignPatternSet.objects.count() == 1
        ps = DesignPatternSet.objects.first()
        assert ps.name == "미니멀 다크"

    def test_pattern_set_has_all_patterns(self):
        ps = DesignPatternSet.objects.first()
        assert ps.memberships.count() == 15

    def test_pattern_set_get_title(self):
        ps = DesignPatternSet.objects.first()
        pattern = ps.get_pattern(PatternCategoryEnum.TITLE)
        assert pattern is not None
        assert pattern.category == PatternCategoryEnum.TITLE

    def test_blank_pattern_has_no_slots(self):
        blank = DesignPattern.objects.get(category=PatternCategoryEnum.BLANK)
        assert blank.slots.count() == 0
