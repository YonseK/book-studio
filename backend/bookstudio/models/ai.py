from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from bookstudio.utils import uuid_key


class AISessionStatusEnum(models.TextChoices):
    PLANNING = "PLANNING", _("Planning")
    REVIEW = "REVIEW", _("Awaiting Review")
    APPROVED = "APPROVED", _("Approved")
    GENERATING = "GENERATING", _("Generating")
    COMPLETE = "COMPLETE", _("Complete")
    FAILED = "FAILED", _("Failed")
    CANCELLED = "CANCELLED", _("Cancelled")


class AISession(models.Model):
    """AI 생성 세션. 하나의 프롬프트 → 하나의 북 생성 과정을 추적."""

    id = models.CharField(
        primary_key=True, max_length=36, default=uuid_key, editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookstudio_ai_sessions",
    )
    book = models.ForeignKey(
        "bookstudio.Book",
        on_delete=models.CASCADE,
        related_name="ai_sessions",
    )
    edition = models.ForeignKey(
        "bookstudio.BookEdition",
        on_delete=models.CASCADE,
        related_name="ai_sessions",
    )

    # ── 입력 ──
    prompt = models.TextField()
    options = models.JSONField(default=dict, blank=True)

    # ── 상태 ──
    status = models.CharField(
        max_length=20,
        choices=AISessionStatusEnum.choices,
        default=AISessionStatusEnum.PLANNING,
    )
    error_message = models.TextField(blank=True)

    # ── 기획서 ──
    plan = models.JSONField(null=True, blank=True)

    # ── 디자인 ──
    pattern_set = models.ForeignKey(
        "bookstudio.DesignPatternSet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    # ── 진행률 ──
    total_pages = models.PositiveSmallIntegerField(default=0)
    completed_pages = models.PositiveSmallIntegerField(default=0)

    # ── 사용량 추적 ──
    model_used = models.CharField(max_length=50, blank=True)
    total_input_tokens = models.PositiveIntegerField(default=0)
    total_output_tokens = models.PositiveIntegerField(default=0)

    # ── Celery 태스크 추적 ──
    celery_task_id = models.CharField(max_length=50, blank=True)

    # ── 타임스탬프 ──
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["book", "-created_at"]),
        ]

    def __str__(self):
        return f"AISession {self.id[:8]} ({self.status})"

    def save(self, **kwargs):
        if not kwargs.get("raw", False):
            self.updated_at = timezone.now()
        super().save(**kwargs)

    def mark_failed(self, message: str):
        self.status = AISessionStatusEnum.FAILED
        self.error_message = message
        self.save(update_fields=["status", "error_message", "updated_at"])

    def mark_complete(self):
        self.status = AISessionStatusEnum.COMPLETE
        self.completed_at = timezone.now()
        self.save(update_fields=["status", "completed_at", "updated_at"])

    def increment_progress(self):
        self.__class__.objects.filter(pk=self.pk).update(
            completed_pages=models.F("completed_pages") + 1
        )

    def add_token_usage(self, input_tokens: int, output_tokens: int):
        self.__class__.objects.filter(pk=self.pk).update(
            total_input_tokens=models.F("total_input_tokens") + input_tokens,
            total_output_tokens=models.F("total_output_tokens") + output_tokens,
        )
