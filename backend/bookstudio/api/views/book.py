from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from bookstudio.models.book import Book, BookEdition, BookCollaborator
from bookstudio.api.serializers.book import (
    BookSerializer,
    BookCreateSerializer,
    BookEditionSerializer,
    BookEditionUpdateSerializer,
    BookCollaboratorSerializer,
    BookCollaboratorCreateSerializer,
)
from bookstudio import conf
from bookstudio.services.cloning import CloneService
from bookstudio.services.publishing import PublishService
from bookstudio.services.permissions import can_edit_book, can_view_book, can_manage_book


def _has_tenant(request):
    """테넌시 활성화 여부 + request.tenant 존재 여부."""
    return conf.TENANT_MODEL and hasattr(request, "tenant")


class BookViewSet(viewsets.ModelViewSet):
    """Book CRUD + clone + publish."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookSerializer

    def get_queryset(self):
        qs = Book.objects.filter(deleted=False).select_related("user")
        if _has_tenant(self.request):
            qs = qs.filter(tenant=self.request.tenant)
        else:
            qs = qs.filter(user=self.request.user)
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return BookCreateSerializer
        return BookSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        extra = {}
        if _has_tenant(request):
            extra["tenant"] = request.tenant
        book = serializer.save(**extra)
        return Response(
            BookSerializer(book).data, status=status.HTTP_201_CREATED
        )

    def perform_destroy(self, instance):
        instance.mark_as_deleted()

    @action(detail=True, methods=["post"])
    def clone(self, request, pk=None):
        """북 딥 클론."""
        book = self.get_object()
        cloned = CloneService.clone_book(book, request.user)
        return Response(BookSerializer(cloned).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        """현재 latest edition을 출판."""
        book = self.get_object()
        edition = book.get_latest_edition()
        if not edition:
            return Response(
                {"detail": "출판할 에디션이 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        new_edition = PublishService.publish(edition)
        return Response(
            BookEditionSerializer(new_edition).data,
            status=status.HTTP_201_CREATED,
        )


class BookEditionViewSet(viewsets.ModelViewSet):
    """BookEdition CRUD (book_pk 중첩)."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookEditionSerializer

    def get_queryset(self):
        book_pk = self.kwargs.get("book_pk")
        qs = BookEdition.objects.filter(book_id=book_pk, deleted=False)
        if _has_tenant(self.request):
            qs = qs.filter(book__tenant=self.request.tenant)
        else:
            qs = qs.filter(book__user=self.request.user)
        return qs

    def get_serializer_class(self):
        if self.action in ("update", "partial_update"):
            return BookEditionUpdateSerializer
        return BookEditionSerializer


class BookCollaboratorViewSet(viewsets.ModelViewSet):
    """BookCollaborator CRUD (book_pk 중첩)."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookCollaboratorSerializer

    def get_queryset(self):
        book_pk = self.kwargs.get("book_pk")
        qs = BookCollaborator.objects.filter(book_id=book_pk, deleted=False)
        if _has_tenant(self.request):
            qs = qs.filter(book__tenant=self.request.tenant)
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return BookCollaboratorCreateSerializer
        return BookCollaboratorSerializer

    def perform_create(self, serializer):
        book_pk = self.kwargs.get("book_pk")
        book = Book.objects.get(pk=book_pk)
        serializer.save(book=book)

    def perform_destroy(self, instance):
        instance.mark_as_deleted()
