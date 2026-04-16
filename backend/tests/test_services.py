import pytest
from django.contrib.auth import get_user_model

from bookstudio.models import (
    Book,
    BookEdition,
    BookLayoutEnum,
    Page,
    Document,
    PageMemo,
    PageMemoComment,
    Panel,
    MediaTypeEnum,
    MediaBank,
    MediaBankTypeEnum,
    Photo,
    WallpaperImage,
    PubBook,
)
from bookstudio.services.cloning import CloneService
from bookstudio.services.publishing import PublishService
from bookstudio.services.permissions import can_edit_book, can_view_book, can_manage_book
from bookstudio.models.book import BookCollaborator, CollaboratorRoleEnum, PrivacyEnum

User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(username="owner", password="pass")


@pytest.fixture
def user2(db):
    return User.objects.create_user(username="collaborator", password="pass")


@pytest.fixture
def user3(db):
    return User.objects.create_user(username="stranger", password="pass")


@pytest.fixture
def full_book(user):
    """페이지, 패널, 문서, 메모, 미디어뱅크를 포함한 전체 북."""
    book = Book.objects.create(user=user, book_layout=BookLayoutEnum.PPTX_WIDE)
    edition = BookEdition.objects.create(book=book, title="원본", version=1, latest=True)

    # 페이지 1: 문서 + 패널 2개 + 메모
    p1 = Page.objects.create(user=user, book_edition=edition, order=0, description="표지")
    Document.objects.create(page=p1, user=user, contents="<h1>표지</h1>")
    Panel.objects.create(user=user, page=p1, media_type=MediaTypeEnum.HL, order=0, headline="제목")
    Panel.objects.create(user=user, page=p1, media_type=MediaTypeEnum.IMG, order=1)
    memo = PageMemo.objects.create(user=user, page=p1, text="검토 필요")
    PageMemoComment.objects.create(user=user, page_memo=memo, comment="확인함")

    # 페이지 2: 패널 1개
    p2 = Page.objects.create(user=user, book_edition=edition, order=1)
    Panel.objects.create(user=user, page=p2, media_type=MediaTypeEnum.TXT, order=0, text="본문")

    # 미디어뱅크
    MediaBank.objects.create(user=user, book=book, bank_type=MediaBankTypeEnum.WALLPAPER, title="배경팩")
    MediaBank.objects.create(user=user, book=book, bank_type=MediaBankTypeEnum.IMAGE, title="이미지팩")

    return book


# ──────────────────── CloneService ────────────────────


class TestClonePanel:
    def test_clone_panel(self, user, full_book):
        edition = full_book.get_latest_edition()
        page = edition.pages.first()
        panel = page.panels.first()
        new_page = Page.objects.create(user=user, book_edition=edition, order=99)
        cloned = CloneService.clone_panel(panel, new_page)

        assert cloned.pk != panel.pk
        assert cloned.page == new_page
        assert cloned.clone_from == panel
        assert cloned.media_type == panel.media_type
        assert cloned.headline == panel.headline


class TestClonePage:
    def test_clone_page_with_children(self, user, full_book):
        edition = full_book.get_latest_edition()
        page = edition.pages.first()
        new_edition = BookEdition.objects.create(
            book=full_book, title="v2", version=2, latest=True
        )

        cloned_page = CloneService.clone_page(page, new_edition)

        assert cloned_page.pk != page.pk
        assert cloned_page.book_edition == new_edition
        assert cloned_page.clone_from == page
        # 패널 복제 확인
        assert cloned_page.panels.count() == page.panels.count()
        # 문서 복제 확인
        assert hasattr(cloned_page, "document")
        assert cloned_page.document.contents == "<h1>표지</h1>"
        # 메모 복제 확인
        assert cloned_page.memos.count() == 1
        assert cloned_page.memos.first().comments.count() == 1


class TestCloneBook:
    def test_deep_clone(self, user, user2, full_book):
        cloned = CloneService.clone_book(full_book, user2)

        assert cloned.pk != full_book.pk
        assert cloned.short_key != full_book.short_key
        assert cloned.user == user2
        assert cloned.clone_from == full_book
        assert cloned.is_published is False

        # 에디션 복제
        cloned_edition = cloned.get_latest_edition()
        assert cloned_edition is not None
        assert cloned_edition.title == "원본"

        # 페이지 복제
        assert cloned_edition.pages.count() == 2

        # 패널 복제
        total_panels = sum(p.panels.count() for p in cloned_edition.pages.all())
        assert total_panels == 3  # 2 + 1

        # 미디어뱅크 복제
        assert cloned.media_banks.count() == 2


# ──────────────────── PublishService ────────────────────


class TestPublishService:
    def test_publish(self, full_book):
        edition = full_book.get_latest_edition()
        new_edition = PublishService.publish(edition)

        # 새 에디터 버전 생성 확인
        assert new_edition.pk != edition.pk
        assert new_edition.latest is True
        assert new_edition.version == 2

        # 기존 에디션 상태 업데이트
        edition.refresh_from_db()
        assert edition.is_published is True
        assert edition.latest is False

        # Book 상태
        full_book.refresh_from_db()
        assert full_book.is_published is True

        # PubBook 생성 확인
        pub_book = PubBook.objects.get(book_edition=edition)
        assert pub_book.latest is True
        assert pub_book.count_pub_pages() == 2

        # PubPanel 확인
        total_pub_panels = sum(pp.panels.count() for pp in pub_book.pages.all())
        assert total_pub_panels == 3

    def test_publish_creates_pub_document(self, full_book):
        edition = full_book.get_latest_edition()
        PublishService.publish(edition)
        pub_book = PubBook.objects.get(book_edition=edition)
        cover = pub_book.pages.order_by("order").first()
        assert hasattr(cover, "document")
        assert cover.document.contents == "<h1>표지</h1>"

    def test_second_publish_retires_previous(self, user, full_book):
        e1 = full_book.get_latest_edition()
        e2 = PublishService.publish(e1)

        # 두 번째 출판을 위해 e2에 페이지 추가
        Page.objects.create(user=user, book_edition=e2, order=2)
        e3 = PublishService.publish(e2)

        pub1 = PubBook.objects.get(book_edition=e1)
        pub2 = PubBook.objects.get(book_edition=e2)
        pub1.refresh_from_db()
        assert pub1.latest is False
        assert pub2.latest is True


# ──────────────────── Permissions ────────────────────


class TestPermissions:
    def test_owner_can_do_everything(self, user, full_book):
        assert can_view_book(user, full_book) is True
        assert can_edit_book(user, full_book) is True
        assert can_manage_book(user, full_book) is True

    def test_editor_can_edit_not_manage(self, user2, full_book):
        BookCollaborator.objects.create(
            user=user2,
            book=full_book,
            role=CollaboratorRoleEnum.EDITOR,
            accepted=True,
        )
        assert can_view_book(user2, full_book) is True
        assert can_edit_book(user2, full_book) is True
        assert can_manage_book(user2, full_book) is False

    def test_viewer_can_view_not_edit(self, user2, full_book):
        BookCollaborator.objects.create(
            user=user2,
            book=full_book,
            role=CollaboratorRoleEnum.VIEWER,
            accepted=True,
        )
        assert can_view_book(user2, full_book) is True
        assert can_edit_book(user2, full_book) is False
        assert can_manage_book(user2, full_book) is False

    def test_stranger_cannot_view_private(self, user3, full_book):
        full_book.privacy = PrivacyEnum.PRIVATE
        full_book.save()
        assert can_view_book(user3, full_book) is False
        assert can_edit_book(user3, full_book) is False

    def test_stranger_can_view_public(self, user3, full_book):
        full_book.privacy = PrivacyEnum.PUBLIC
        full_book.save()
        assert can_view_book(user3, full_book) is True
        assert can_edit_book(user3, full_book) is False

    def test_unaccepted_collaborator_cannot_edit(self, user2, full_book):
        BookCollaborator.objects.create(
            user=user2,
            book=full_book,
            role=CollaboratorRoleEnum.EDITOR,
            accepted=False,
        )
        assert can_edit_book(user2, full_book) is False

    def test_deleted_collaborator_cannot_edit(self, user2, full_book):
        BookCollaborator.objects.create(
            user=user2,
            book=full_book,
            role=CollaboratorRoleEnum.EDITOR,
            accepted=True,
            deleted=True,
        )
        assert can_edit_book(user2, full_book) is False

    def test_manager_can_manage(self, user2, full_book):
        BookCollaborator.objects.create(
            user=user2,
            book=full_book,
            role=CollaboratorRoleEnum.MANAGER,
            accepted=True,
        )
        assert can_manage_book(user2, full_book) is True
