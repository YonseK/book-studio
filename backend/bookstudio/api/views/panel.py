from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from bookstudio.models.panel import Panel
from bookstudio.api.serializers.panel import (
    PanelSerializer,
    PanelCreateSerializer,
    PanelUpdateSerializer,
    PanelSortSerializer,
)
from bookstudio.services.cloning import CloneService


class PanelViewSet(viewsets.ModelViewSet):
    """Panel CRUD + sort + clone."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PanelSerializer

    def get_queryset(self):
        page_pk = self.kwargs.get("page_pk")
        if page_pk:
            return Panel.objects.filter(
                page_id=page_pk, deleted=False
            ).select_related("image")
        return Panel.objects.filter(
            user=self.request.user, deleted=False
        )

    def get_serializer_class(self):
        if self.action == "create":
            return PanelCreateSerializer
        if self.action in ("update", "partial_update"):
            return PanelUpdateSerializer
        return PanelSerializer

    def perform_destroy(self, instance):
        instance.mark_as_deleted()

    @action(detail=False, methods=["post"])
    def sort(self, request, **kwargs):
        """패널 순서 변경."""
        serializer = PanelSortSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        panel_ids = serializer.validated_data["panel_ids"]
        for order, panel_id in enumerate(panel_ids):
            Panel.objects.filter(pk=panel_id).update(order=order)
        return Response({"detail": "순서 변경 완료"})

    @action(detail=True, methods=["post"])
    def clone(self, request, pk=None, **kwargs):
        """패널 복제."""
        panel = self.get_object()
        cloned = CloneService.clone_panel(panel, panel.page)
        return Response(PanelSerializer(cloned).data, status=status.HTTP_201_CREATED)
