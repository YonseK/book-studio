from rest_framework import viewsets, permissions, parsers

from bookstudio import conf
from bookstudio.models.media import Photo, WallpaperImage
from bookstudio.models.media_bank import MediaBank, MediaGallery
from bookstudio.models.item_bank import PubItem
from bookstudio.api.serializers.media import (
    PhotoSerializer,
    PhotoUploadSerializer,
    WallpaperImageSerializer,
    WallpaperImageUploadSerializer,
    MediaBankSerializer,
    MediaBankCreateSerializer,
    MediaGallerySerializer,
    PubItemSerializer,
    PubItemUploadSerializer,
)


class PhotoViewSet(viewsets.ModelViewSet):
    """Photo 업로드/조회."""

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    serializer_class = PhotoSerializer

    def get_queryset(self):
        qs = Photo.objects.filter(is_active=True)
        if conf.TENANT_MODEL and hasattr(self.request, "tenant"):
            qs = qs.filter(user__tenant_memberships__tenant=self.request.tenant)
        else:
            qs = qs.filter(user=self.request.user)
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return PhotoUploadSerializer
        return PhotoSerializer


class WallpaperImageViewSet(viewsets.ModelViewSet):
    """WallpaperImage 업로드/조회."""

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    serializer_class = WallpaperImageSerializer

    def get_queryset(self):
        return WallpaperImage.objects.filter(user=self.request.user, is_active=True)

    def get_serializer_class(self):
        if self.action == "create":
            return WallpaperImageUploadSerializer
        return WallpaperImageSerializer


class MediaBankViewSet(viewsets.ModelViewSet):
    """MediaBank CRUD (book_pk 중첩)."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MediaBankSerializer

    def get_queryset(self):
        book_pk = self.kwargs.get("book_pk")
        if book_pk:
            return MediaBank.objects.filter(book_id=book_pk)
        return MediaBank.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return MediaBankCreateSerializer
        return MediaBankSerializer


class MediaGalleryViewSet(viewsets.ModelViewSet):
    """MediaGallery CRUD."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MediaGallerySerializer

    def get_queryset(self):
        return MediaGallery.objects.filter(user=self.request.user, is_active=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PubItemViewSet(viewsets.ModelViewSet):
    """PubItem 업로드/조회."""

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    serializer_class = PubItemSerializer

    def get_queryset(self):
        return PubItem.objects.filter(user=self.request.user, is_active=True)

    def get_serializer_class(self):
        if self.action == "create":
            return PubItemUploadSerializer
        return PubItemSerializer
