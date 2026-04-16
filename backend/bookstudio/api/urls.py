from django.urls import path, include
from rest_framework.routers import DefaultRouter

from bookstudio.api.views.book import (
    BookViewSet,
    BookEditionViewSet,
    BookCollaboratorViewSet,
)
from bookstudio.api.views.page import (
    PageViewSet,
    DocumentViewSet,
    PageMemoViewSet,
    PageMemoCommentViewSet,
)
from bookstudio.api.views.panel import PanelViewSet
from bookstudio.api.views.media import (
    PhotoViewSet,
    WallpaperImageViewSet,
    MediaBankViewSet,
    MediaGalleryViewSet,
    PubItemViewSet,
)

app_name = "bookstudio"

router = DefaultRouter()

# ──── Top-level ────
router.register(r"books", BookViewSet, basename="book")
router.register(r"photos", PhotoViewSet, basename="photo")
router.register(r"wallpapers", WallpaperImageViewSet, basename="wallpaper")
router.register(r"galleries", MediaGalleryViewSet, basename="gallery")
router.register(r"items", PubItemViewSet, basename="pubitem")

# ──── Nested under book ────
book_router = DefaultRouter()
book_router.register(r"editions", BookEditionViewSet, basename="book-edition")
book_router.register(r"collaborators", BookCollaboratorViewSet, basename="book-collaborator")
book_router.register(r"media-banks", MediaBankViewSet, basename="book-mediabank")

# ──── Nested under edition ────
edition_router = DefaultRouter()
edition_router.register(r"pages", PageViewSet, basename="edition-page")

# ──── Nested under page ────
page_router = DefaultRouter()
page_router.register(r"panels", PanelViewSet, basename="page-panel")
page_router.register(r"documents", DocumentViewSet, basename="page-document")
page_router.register(r"memos", PageMemoViewSet, basename="page-memo")

# ──── Nested under memo ────
memo_router = DefaultRouter()
memo_router.register(r"comments", PageMemoCommentViewSet, basename="memo-comment")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "books/<str:book_pk>/",
        include((book_router.urls, "book-nested")),
    ),
    path(
        "books/<str:book_pk>/editions/<str:edition_pk>/",
        include((edition_router.urls, "edition-nested")),
    ),
    path(
        "pages/<str:page_pk>/",
        include((page_router.urls, "page-nested")),
    ),
    path(
        "memos/<str:memo_pk>/",
        include((memo_router.urls, "memo-nested")),
    ),
]
