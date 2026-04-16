import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from bookstudio.models import (
    Book,
    BookEdition,
    BookCollaborator,
    BookLayoutEnum,
    BookModeEnum,
    CollaboratorRoleEnum,
    Page,
    Document,
    PageMemo,
    PageMemoComment,
    BackgroundTypeEnum,
    Panel,
    MediaTypeEnum,
    Photo,
    WallpaperImage,
    MediaBank,
    MediaBankTypeEnum,
    MediaGallery,
    MediaGalleryMembership,
    MediaGalleryMember,
    PubItem,
    PubBook,
    PubPage,
    PubPanel,
    PubDocument,
)

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="pass1234")


@pytest.fixture
def user2(db):
    return User.objects.create_user(username="testuser2", password="pass1234")


@pytest.fixture
def book(user):
    return Book.objects.create(user=user, book_layout=BookLayoutEnum.PPTX_WIDE)


@pytest.fixture
def edition(book):
    return BookEdition.objects.create(book=book, title="Test Edition", version=1, latest=True)


@pytest.fixture
def page(user, edition):
    return Page.objects.create(user=user, book_edition=edition, order=0)


@pytest.fixture
def panel(user, page):
    return Panel.objects.create(user=user, page=page, media_type=MediaTypeEnum.TXT, order=0)


# ──────────────────── Book 모델 ────────────────────


class TestBook:
    def test_create(self, book):
        assert book.pk is not None
        assert len(book.short_key) == 8
        assert book.book_layout == BookLayoutEnum.PPTX_WIDE
        assert book.is_published is False
        assert book.deleted is False

    def test_str(self, book):
        assert book.short_key in str(book)

    def test_mark_as_deleted(self, book):
        book.mark_as_deleted()
        book.refresh_from_db()
        assert book.deleted is True

    def test_touch(self, book):
        old = book.updated_at
        book.touch()
        book.refresh_from_db()
        assert book.updated_at >= old

    def test_get_latest_edition(self, book, edition):
        assert book.get_latest_edition() == edition

    def test_get_latest_edition_none(self, book):
        assert book.get_latest_edition() is None

    def test_get_latest_title(self, book, edition):
        assert book.get_latest_title() == "Test Edition"

    def test_is_scrap(self, user):
        scrap_book = Book.objects.create(user=user, book_mode=BookModeEnum.VIDEO_ALBUM)
        assert scrap_book.is_scrap() is True

        normal_book = Book.objects.create(user=user, book_mode=BookModeEnum.BOOK)
        assert normal_book.is_scrap() is False

    def test_default_layout(self, user):
        b = Book.objects.create(user=user)
        assert b.book_layout == BookLayoutEnum.PPTX_WIDE


# ──────────────────── BookEdition 모델 ────────────────────


class TestBookEdition:
    def test_create(self, edition):
        assert edition.pk is not None
        assert edition.latest is True
        assert edition.version == 1

    def test_str(self, edition):
        assert "v1" in str(edition)

    def test_set_as_latest(self, book):
        e1 = BookEdition.objects.create(book=book, version=1, latest=True)
        e2 = BookEdition.objects.create(book=book, version=2, latest=False)
        e2.set_as_latest()
        e1.refresh_from_db()
        assert e1.latest is False
        assert e2.latest is True

    def test_latest_version_number(self, book):
        BookEdition.objects.create(book=book, version=1)
        BookEdition.objects.create(book=book, version=3)
        e = BookEdition.objects.filter(book=book).first()
        assert e.latest_version_number() == 3

    def test_count_pages(self, user, edition):
        Page.objects.create(user=user, book_edition=edition, order=0)
        Page.objects.create(user=user, book_edition=edition, order=1)
        assert edition.count_pages() == 2

    def test_get_cover_page(self, user, edition):
        p2 = Page.objects.create(user=user, book_edition=edition, order=1)
        p1 = Page.objects.create(user=user, book_edition=edition, order=0)
        assert edition.get_cover_page() == p1

    def test_touch_cascades_to_book(self, edition):
        old_book_update = edition.book.updated_at
        edition.touch()
        edition.book.refresh_from_db()
        assert edition.book.updated_at >= old_book_update

    def test_manager_get_latest(self, book, edition):
        assert BookEdition.objects.get_latest(book=book) == edition
        assert BookEdition.objects.get_latest(book=None) is None


# ──────────────────── BookCollaborator 모델 ────────────────────


class TestBookCollaborator:
    def test_create(self, book, user2):
        collab = BookCollaborator.objects.create(
            user=user2, book=book, role=CollaboratorRoleEnum.EDITOR
        )
        assert collab.pk is not None
        assert collab.accepted is False

    def test_mark_as_deleted(self, book, user2):
        collab = BookCollaborator.objects.create(user=user2, book=book)
        collab.mark_as_deleted()
        collab.refresh_from_db()
        assert collab.deleted is True


# ──────────────────── Page 모델 ────────────────────


class TestPage:
    def test_create(self, page):
        assert page.pk is not None
        assert len(page.short_key) == 8
        assert page.background_type == BackgroundTypeEnum.COLOR
        assert page.background_color == "#ffffff"

    def test_mark_as_deleted(self, page):
        page.mark_as_deleted()
        page.refresh_from_db()
        assert page.deleted is True

    def test_count_panels(self, user, page):
        Panel.objects.create(user=user, page=page, order=0)
        Panel.objects.create(user=user, page=page, order=1)
        assert page.count_panels() == 2

    def test_touch_cascades(self, page):
        old_edition_update = page.book_edition.updated_at
        page.touch()
        page.book_edition.refresh_from_db()
        assert page.book_edition.updated_at >= old_edition_update


# ──────────────────── Document 모델 ────────────────────


class TestDocument:
    def test_create(self, user, page):
        doc = Document.objects.create(
            page=page, user=user, contents="<p>Hello</p>", edit_type="wysiwyg"
        )
        assert doc.pk is not None
        assert doc.contents == "<p>Hello</p>"

    def test_one_to_one(self, user, page):
        Document.objects.create(page=page, user=user)
        with pytest.raises(Exception):
            Document.objects.create(page=page, user=user)


# ──────────────────── PageMemo / PageMemoComment ────────────────────


class TestPageMemo:
    def test_create(self, user, page):
        memo = PageMemo.objects.create(user=user, page=page, text="메모 테스트")
        assert memo.pk is not None
        assert memo.private is False

    def test_comments(self, user, page):
        memo = PageMemo.objects.create(user=user, page=page, text="메모")
        c = PageMemoComment.objects.create(user=user, page_memo=memo, comment="댓글")
        assert memo.comments.count() == 1
        assert c.page_memo == memo


# ──────────────────── Panel 모델 ────────────────────


class TestPanel:
    def test_create(self, panel):
        assert panel.pk is not None
        assert panel.media_type == MediaTypeEnum.TXT

    def test_style_defaults(self, panel):
        assert panel.width == 300.0
        assert panel.height == 200.0
        assert panel.z_index == 0
        assert panel.opacity == 1.0
        assert panel.font_size == 16

    def test_mark_as_deleted(self, panel):
        panel.mark_as_deleted()
        panel.refresh_from_db()
        assert panel.deleted is True

    def test_get_book_layout(self, panel):
        assert panel.get_book_layout() == BookLayoutEnum.PPTX_WIDE

    def test_touch_cascades(self, panel):
        old = panel.page.updated_at
        panel.touch()
        panel.page.refresh_from_db()
        assert panel.page.updated_at >= old

    def test_all_media_types(self):
        assert len(MediaTypeEnum.choices) == 14


# ──────────────────── Photo 모델 ────────────────────


class TestPhoto:
    def test_create(self, user):
        photo = Photo.objects.create(user=user, title="test.jpg", width=800, height=600)
        assert photo.pk is not None
        assert photo.width == 800

    def test_url_methods_empty(self, user):
        photo = Photo.objects.create(user=user)
        assert photo.get_image_url() == ""
        assert photo.get_image_view_url() == ""


# ──────────────────── WallpaperImage 모델 ────────────────────


class TestWallpaperImage:
    def test_create(self, user):
        wp = WallpaperImage.objects.create(user=user, wallpaper_layout="MBOOK")
        assert wp.pk is not None
        assert wp.wallpaper_layout == "MBOOK"


# ──────────────────── MediaBank 모델 ────────────────────


class TestMediaBank:
    def test_create(self, user, book):
        mb = MediaBank.objects.create(
            user=user, book=book, bank_type=MediaBankTypeEnum.WALLPAPER, title="배경팩"
        )
        assert mb.pk is not None
        assert mb.bank_type == "WP"

    def test_book_relation(self, user, book):
        MediaBank.objects.create(user=user, book=book, bank_type=MediaBankTypeEnum.IMAGE)
        MediaBank.objects.create(user=user, book=book, bank_type=MediaBankTypeEnum.WALLPAPER)
        assert book.media_banks.count() == 2


# ──────────────────── MediaGallery 관련 모델 ────────────────────


class TestMediaGallery:
    def test_create(self, user):
        gallery = MediaGallery.objects.create(user=user, title="내 갤러리")
        assert gallery.pk is not None

    def test_membership_and_member(self, user):
        gallery = MediaGallery.objects.create(user=user, title="갤러리")
        membership = MediaGalleryMembership.objects.create(user=user, name="기본")
        member = MediaGalleryMember.objects.create(
            user=user, membership=membership, media_gallery=gallery
        )
        assert membership.members.count() == 1
        assert gallery.members.count() == 1


# ──────────────────── PubItem 모델 ────────────────────


class TestPubItem:
    def test_create(self, user):
        item = PubItem.objects.create(user=user, title="아이템", width=100, height=100)
        assert item.pk is not None
        assert item.title == "아이템"


# ──────────────────── Publishing 모델 ────────────────────


class TestPublishing:
    def test_pub_book_create(self, edition):
        pub = PubBook.objects.create(book_edition=edition)
        assert pub.pk is not None
        assert pub.latest is True

    def test_pub_book_set_as_latest(self, book):
        e1 = BookEdition.objects.create(book=book, version=1)
        e2 = BookEdition.objects.create(book=book, version=2)
        p1 = PubBook.objects.create(book_edition=e1, latest=True)
        p2 = PubBook.objects.create(book_edition=e2, latest=False)
        p2.set_as_latest()
        p1.refresh_from_db()
        assert p1.latest is False
        assert p2.latest is True

    def test_pub_page_create(self, user, edition):
        pub_book = PubBook.objects.create(book_edition=edition)
        page = Page.objects.create(user=user, book_edition=edition, order=0)
        pub_page = PubPage.objects.create(pub_book=pub_book, page=page, order=0)
        assert pub_page.pk is not None
        assert pub_book.count_pub_pages() == 1

    def test_pub_panel_create(self, user, edition):
        pub_book = PubBook.objects.create(book_edition=edition)
        page = Page.objects.create(user=user, book_edition=edition, order=0)
        pub_page = PubPage.objects.create(pub_book=pub_book, page=page, order=0)
        panel = Panel.objects.create(user=user, page=page, media_type=MediaTypeEnum.IMG, order=0)
        pub_panel = PubPanel.objects.create(pub_page=pub_page, panel=panel, order=0)
        assert pub_panel.pk is not None
        assert pub_page.panels.count() == 1

    def test_pub_document_create(self, user, edition):
        pub_book = PubBook.objects.create(book_edition=edition)
        page = Page.objects.create(user=user, book_edition=edition, order=0)
        doc = Document.objects.create(page=page, user=user, contents="<p>test</p>")
        pub_page = PubPage.objects.create(pub_book=pub_book, page=page, order=0)
        pub_doc = PubDocument.objects.create(
            pub_page=pub_page, document=doc, contents=doc.contents
        )
        assert pub_doc.pk is not None
        assert pub_doc.contents == "<p>test</p>"

    def test_pub_book_manager_get_latest(self, book, edition):
        pub = PubBook.objects.create(book_edition=edition, latest=True)
        assert PubBook.objects.get_latest(book=book) == pub
        assert PubBook.objects.get_latest(book=None) is None

    def test_pub_book_get_cover_page(self, user, edition):
        pub_book = PubBook.objects.create(book_edition=edition)
        page1 = Page.objects.create(user=user, book_edition=edition, order=1)
        page0 = Page.objects.create(user=user, book_edition=edition, order=0)
        PubPage.objects.create(pub_book=pub_book, page=page1, order=1)
        pp0 = PubPage.objects.create(pub_book=pub_book, page=page0, order=0)
        assert pub_book.get_cover_page() == pp0
