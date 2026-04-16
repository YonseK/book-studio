import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from bookstudio.models import (
    Book,
    BookEdition,
    BookCollaborator,
    BookLayoutEnum,
    Page,
    Panel,
    Document,
    PageMemo,
    PageMemoComment,
    MediaTypeEnum,
    MediaBank,
    MediaBankTypeEnum,
    Photo,
    WallpaperImage,
    MediaGallery,
    PubItem,
)

User = get_user_model()
BASE = "/api/studio"


@pytest.fixture
def user(db):
    return User.objects.create_user(username="apiuser", password="pass1234")


@pytest.fixture
def user2(db):
    return User.objects.create_user(username="apiuser2", password="pass1234")


@pytest.fixture
def client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.fixture
def anon_client():
    return APIClient()


@pytest.fixture
def book(user):
    b = Book.objects.create(user=user, book_layout=BookLayoutEnum.PPTX_WIDE)
    BookEdition.objects.create(book=b, title="에디션1", version=1, latest=True)
    return b


@pytest.fixture
def edition(book):
    return book.get_latest_edition()


@pytest.fixture
def page(user, edition):
    return Page.objects.create(user=user, book_edition=edition, order=0)


@pytest.fixture
def panel(user, page):
    return Panel.objects.create(user=user, page=page, media_type=MediaTypeEnum.TXT, order=0)


# ──────────────────── 인증 ────────────────────


class TestAuth:
    def test_unauthenticated_returns_403(self, anon_client):
        resp = anon_client.get(f"{BASE}/books/")
        assert resp.status_code == 403


# ──────────────────── Book API ────────────────────


class TestBookAPI:
    def test_list(self, client, book):
        resp = client.get(f"{BASE}/books/")
        assert resp.status_code == 200
        assert len(resp.data) == 1

    def test_create(self, client):
        resp = client.post(f"{BASE}/books/", {"book_layout": "PPTX_WIDE"})
        assert resp.status_code == 201
        book_id = resp.data["id"]
        # 기본 에디션 자동 생성 확인
        assert BookEdition.objects.filter(book_id=book_id).count() == 1

    def test_create_custom_layout_requires_dimensions(self, client):
        resp = client.post(f"{BASE}/books/", {"book_layout": "CUSTOM"})
        assert resp.status_code == 400

    def test_create_custom_layout_ok(self, client):
        resp = client.post(
            f"{BASE}/books/",
            {"book_layout": "CUSTOM", "custom_width": 1920, "custom_height": 1080},
        )
        assert resp.status_code == 201

    def test_retrieve(self, client, book):
        resp = client.get(f"{BASE}/books/{book.pk}/")
        assert resp.status_code == 200
        assert resp.data["short_key"] == book.short_key

    def test_update(self, client, book):
        resp = client.patch(
            f"{BASE}/books/{book.pk}/",
            {"book_layout": "CD"},
            format="json",
        )
        assert resp.status_code == 200
        book.refresh_from_db()
        assert book.book_layout == "CD"

    def test_delete_soft(self, client, book):
        resp = client.delete(f"{BASE}/books/{book.pk}/")
        assert resp.status_code == 204
        book.refresh_from_db()
        assert book.deleted is True

    def test_clone(self, client, book):
        resp = client.post(f"{BASE}/books/{book.pk}/clone/")
        assert resp.status_code == 201
        assert resp.data["id"] != book.pk

    def test_publish(self, client, book, page, panel):
        resp = client.post(f"{BASE}/books/{book.pk}/publish/")
        assert resp.status_code == 201
        assert resp.data["version"] == 2

    def test_other_user_cannot_see(self, user2, book):
        c = APIClient()
        c.force_authenticate(user=user2)
        resp = c.get(f"{BASE}/books/")
        assert len(resp.data) == 0


# ──────────────────── BookEdition API ────────────────────


class TestBookEditionAPI:
    def test_list(self, client, book, edition):
        resp = client.get(f"{BASE}/books/{book.pk}/editions/")
        assert resp.status_code == 200
        assert len(resp.data) == 1

    def test_update_title(self, client, book, edition):
        resp = client.patch(
            f"{BASE}/books/{book.pk}/editions/{edition.pk}/",
            {"title": "새 제목"},
            format="json",
        )
        assert resp.status_code == 200
        edition.refresh_from_db()
        assert edition.title == "새 제목"


# ──────────────────── BookCollaborator API ────────────────────


class TestCollaboratorAPI:
    def test_create_with_email(self, client, book, user2):
        resp = client.post(
            f"{BASE}/books/{book.pk}/collaborators/",
            {"invitation_email": "test@example.com", "role": "EDITOR"},
            format="json",
        )
        assert resp.status_code == 201

    def test_create_requires_user_or_email(self, client, book):
        resp = client.post(
            f"{BASE}/books/{book.pk}/collaborators/",
            {"role": "VIEWER"},
            format="json",
        )
        assert resp.status_code == 400


# ──────────────────── Page API ────────────────────


class TestPageAPI:
    def test_list(self, client, book, edition, page):
        resp = client.get(
            f"{BASE}/books/{book.pk}/editions/{edition.pk}/pages/"
        )
        assert resp.status_code == 200
        assert len(resp.data) == 1

    def test_create(self, client, book, edition):
        resp = client.post(
            f"{BASE}/books/{book.pk}/editions/{edition.pk}/pages/",
            {"book_edition": edition.pk, "background_color": "#000000"},
            format="json",
        )
        assert resp.status_code == 201
        assert resp.data["background_color"] == "#000000"

    def test_sort(self, client, user, book, edition):
        p1 = Page.objects.create(user=user, book_edition=edition, order=0)
        p2 = Page.objects.create(user=user, book_edition=edition, order=1)
        resp = client.post(
            f"{BASE}/books/{book.pk}/editions/{edition.pk}/pages/sort/",
            {"page_ids": [p2.pk, p1.pk]},
            format="json",
        )
        assert resp.status_code == 200
        p1.refresh_from_db()
        p2.refresh_from_db()
        assert p2.order == 0
        assert p1.order == 1

    def test_clone(self, client, book, edition, page, panel):
        resp = client.post(
            f"{BASE}/books/{book.pk}/editions/{edition.pk}/pages/{page.pk}/clone/"
        )
        assert resp.status_code == 201
        assert resp.data["id"] != page.pk

    def test_delete(self, client, book, edition, page):
        resp = client.delete(
            f"{BASE}/books/{book.pk}/editions/{edition.pk}/pages/{page.pk}/"
        )
        assert resp.status_code == 204
        page.refresh_from_db()
        assert page.deleted is True


# ──────────────────── Panel API ────────────────────


class TestPanelAPI:
    def test_list(self, client, page, panel):
        resp = client.get(f"{BASE}/pages/{page.pk}/panels/")
        assert resp.status_code == 200
        assert len(resp.data) == 1

    def test_create(self, client, page):
        resp = client.post(
            f"{BASE}/pages/{page.pk}/panels/",
            {
                "page": page.pk,
                "media_type": "IMG",
                "left": 100,
                "top": 50,
                "width": 400,
                "height": 300,
            },
            format="json",
        )
        assert resp.status_code == 201
        assert resp.data["media_type"] == "IMG"
        assert resp.data["left"] == 100

    def test_update_position(self, client, page, panel):
        resp = client.patch(
            f"{BASE}/pages/{page.pk}/panels/{panel.pk}/",
            {"left": 200, "top": 100, "width": 500},
            format="json",
        )
        assert resp.status_code == 200
        panel.refresh_from_db()
        assert panel.left == 200
        assert panel.width == 500.0

    def test_sort(self, client, user, page):
        p1 = Panel.objects.create(user=user, page=page, media_type=MediaTypeEnum.TXT, order=0)
        p2 = Panel.objects.create(user=user, page=page, media_type=MediaTypeEnum.IMG, order=1)
        resp = client.post(
            f"{BASE}/pages/{page.pk}/panels/sort/",
            {"panel_ids": [p2.pk, p1.pk]},
            format="json",
        )
        assert resp.status_code == 200
        p1.refresh_from_db()
        p2.refresh_from_db()
        assert p2.order == 0
        assert p1.order == 1

    def test_clone(self, client, page, panel):
        resp = client.post(f"{BASE}/pages/{page.pk}/panels/{panel.pk}/clone/")
        assert resp.status_code == 201
        assert resp.data["id"] != panel.pk

    def test_delete(self, client, page, panel):
        resp = client.delete(f"{BASE}/pages/{page.pk}/panels/{panel.pk}/")
        assert resp.status_code == 204
        panel.refresh_from_db()
        assert panel.deleted is True


# ──────────────────── Document API ────────────────────


class TestDocumentAPI:
    def test_create_and_list(self, client, page):
        resp = client.post(
            f"{BASE}/pages/{page.pk}/documents/",
            {"page": page.pk, "contents": "<p>Hello</p>", "edit_type": "wysiwyg"},
            format="json",
        )
        assert resp.status_code == 201

        resp = client.get(f"{BASE}/pages/{page.pk}/documents/")
        assert resp.status_code == 200
        assert len(resp.data) == 1


# ──────────────────── PageMemo API ────────────────────


class TestPageMemoAPI:
    def test_create_and_list(self, client, page):
        resp = client.post(
            f"{BASE}/pages/{page.pk}/memos/",
            {"page": page.pk, "text": "메모입니다"},
            format="json",
        )
        assert resp.status_code == 201
        memo_id = resp.data["id"]

        resp = client.get(f"{BASE}/pages/{page.pk}/memos/")
        assert len(resp.data) == 1

    def test_memo_comment(self, client, user, page):
        memo = PageMemo.objects.create(user=user, page=page, text="메모")
        resp = client.post(
            f"{BASE}/memos/{memo.pk}/comments/",
            {"page_memo": memo.pk, "comment": "댓글입니다"},
            format="json",
        )
        assert resp.status_code == 201

        resp = client.get(f"{BASE}/memos/{memo.pk}/comments/")
        assert len(resp.data) == 1


# ──────────────────── MediaBank API ────────────────────


class TestMediaBankAPI:
    def test_list_and_create(self, client, user, book):
        resp = client.post(
            f"{BASE}/books/{book.pk}/media-banks/",
            {"book": book.pk, "bank_type": "WP", "title": "배경팩"},
            format="json",
        )
        assert resp.status_code == 201

        resp = client.get(f"{BASE}/books/{book.pk}/media-banks/")
        assert len(resp.data) == 1


# ──────────────────── MediaGallery API ────────────────────


class TestMediaGalleryAPI:
    def test_create_and_list(self, client):
        resp = client.post(
            f"{BASE}/galleries/",
            {"title": "내 갤러리"},
            format="json",
        )
        assert resp.status_code == 201

        resp = client.get(f"{BASE}/galleries/")
        assert len(resp.data) == 1


# ──────────────────── Photo API (메타만, 업로드 제외) ────────────────────


class TestPhotoAPI:
    def test_list_empty(self, client):
        resp = client.get(f"{BASE}/photos/")
        assert resp.status_code == 200
        assert len(resp.data) == 0


# ──────────────────── PubItem API ────────────────────


class TestPubItemAPI:
    def test_list_empty(self, client):
        resp = client.get(f"{BASE}/items/")
        assert resp.status_code == 200
        assert len(resp.data) == 0
