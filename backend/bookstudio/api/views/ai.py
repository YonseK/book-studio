from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from bookstudio.models.ai import AISession, AISessionStatusEnum
from bookstudio.models.design_pattern import (
    DesignPattern,
    DesignPatternSlot,
    DesignPatternSet,
)
from bookstudio.api.serializers.ai import (
    AISessionSerializer,
    AISessionCreateSerializer,
    DesignPatternSerializer,
    DesignPatternListSerializer,
    DesignPatternSlotSerializer,
    DesignPatternSetSerializer,
    DesignPatternSetCreateSerializer,
)
from bookstudio.services.ai.runner import start_planning, start_generation


class DesignPatternViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = DesignPattern.objects.filter(is_active=True)
        category = self.request.query_params.get("category")
        if category:
            qs = qs.filter(category=category)
        target_layout = self.request.query_params.get("target_layout")
        if target_layout:
            qs = qs.filter(target_layout=target_layout)
        source = self.request.query_params.get("source")
        if source:
            qs = qs.filter(source=source)
        tags = self.request.query_params.get("tags")
        if tags:
            tag_list = [t.strip() for t in tags.split(",")]
            qs = qs.filter(tags__contains=tag_list)
        return qs.prefetch_related("slots")

    def get_serializer_class(self):
        if self.action == "list":
            return DesignPatternListSerializer
        return DesignPatternSerializer


class DesignPatternSetViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = DesignPatternSet.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return DesignPatternSetCreateSerializer
        return DesignPatternSetSerializer


class DesignPatternSlotViewSet(viewsets.ModelViewSet):
    """패턴 하위 슬롯 CRUD."""

    permission_classes = [IsAuthenticated]
    serializer_class = DesignPatternSlotSerializer

    def get_queryset(self):
        return DesignPatternSlot.objects.filter(
            pattern_id=self.kwargs["pattern_pk"]
        )

    def perform_create(self, serializer):
        serializer.save(pattern_id=self.kwargs["pattern_pk"])


# ── AISession ──


class AISessionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post"]

    def get_queryset(self):
        return AISession.objects.filter(user=self.request.user).select_related(
            "book", "edition", "pattern_set",
        )

    def get_serializer_class(self):
        if self.action == "create":
            return AISessionCreateSerializer
        return AISessionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = serializer.save(user=request.user)
        start_planning(session)
        # 동기 모드에서는 planning 완료 후 상태가 변경되므로 reload
        session.refresh_from_db()
        return Response(
            AISessionSerializer(session).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        session = self.get_object()

        if session.status != AISessionStatusEnum.REVIEW:
            return Response(
                {"error": f"Cannot approve session in {session.status} status"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if "plan" in request.data:
            session.plan = request.data["plan"]
        if "pattern_set_id" in request.data:
            session.pattern_set_id = request.data["pattern_set_id"]

        session.status = AISessionStatusEnum.APPROVED
        session.save(update_fields=["plan", "pattern_set", "status", "updated_at"])

        start_generation(session)

        return Response(AISessionSerializer(session).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        session = self.get_object()

        if session.status in (
            AISessionStatusEnum.COMPLETE,
            AISessionStatusEnum.CANCELLED,
        ):
            return Response(
                {"error": "Session already completed or cancelled"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if session.celery_task_id:
            try:
                from celery.result import AsyncResult
                AsyncResult(session.celery_task_id).revoke(terminate=True)
            except ImportError:
                pass

        session.status = AISessionStatusEnum.CANCELLED
        session.save(update_fields=["status", "updated_at"])

        return Response(AISessionSerializer(session).data)
