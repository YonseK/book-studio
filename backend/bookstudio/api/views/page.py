from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from bookstudio.models.page import Page, Document, PageMemo, PageMemoComment
from bookstudio.api.serializers.page import (
    PageSerializer,
    PageCreateSerializer,
    PageUpdateSerializer,
    PageSortSerializer,
    DocumentSerializer,
    DocumentCreateSerializer,
    PageMemoSerializer,
    PageMemoCommentSerializer,
)
from bookstudio.services.cloning import CloneService


class PageViewSet(viewsets.ModelViewSet):
    """Page CRUD + sort + clone."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PageSerializer

    def get_queryset(self):
        edition_pk = self.kwargs.get("edition_pk")
        if edition_pk:
            return Page.objects.filter(
                book_edition_id=edition_pk, deleted=False
            ).select_related("wallpaper", "wallpaper_image")
        return Page.objects.filter(
            user=self.request.user, deleted=False
        )

    def get_serializer_class(self):
        if self.action == "create":
            return PageCreateSerializer
        if self.action in ("update", "partial_update"):
            return PageUpdateSerializer
        return PageSerializer

    def perform_destroy(self, instance):
        instance.mark_as_deleted()

    @action(detail=False, methods=["post"])
    def sort(self, request, **kwargs):
        """페이지 순서 변경."""
        serializer = PageSortSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        page_ids = serializer.validated_data["page_ids"]
        for order, page_id in enumerate(page_ids):
            Page.objects.filter(pk=page_id).update(order=order)
        return Response({"detail": "순서 변경 완료"})

    @action(detail=True, methods=["post"])
    def clone(self, request, pk=None, **kwargs):
        """페이지 복제."""
        page = self.get_object()
        edition = page.book_edition
        cloned = CloneService.clone_page(page, edition, user=request.user)
        return Response(PageSerializer(cloned).data, status=status.HTTP_201_CREATED)


class DocumentViewSet(viewsets.ModelViewSet):
    """Document CRUD."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DocumentSerializer

    def get_queryset(self):
        page_pk = self.kwargs.get("page_pk")
        if page_pk:
            return Document.objects.filter(page_id=page_pk)
        return Document.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return DocumentCreateSerializer
        return DocumentSerializer


class PageMemoViewSet(viewsets.ModelViewSet):
    """PageMemo CRUD."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PageMemoSerializer

    def get_queryset(self):
        page_pk = self.kwargs.get("page_pk")
        if page_pk:
            return PageMemo.objects.filter(page_id=page_pk, is_active=True)
        return PageMemo.objects.filter(user=self.request.user, is_active=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PageMemoCommentViewSet(viewsets.ModelViewSet):
    """PageMemoComment CRUD."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PageMemoCommentSerializer

    def get_queryset(self):
        memo_pk = self.kwargs.get("memo_pk")
        if memo_pk:
            return PageMemoComment.objects.filter(page_memo_id=memo_pk)
        return PageMemoComment.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
