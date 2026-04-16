from django.conf import settings
from django.db import models
from django.utils import timezone

from bookstudio.utils import uuid_key
from bookstudio.models.media import AbstractBasePhoto


# ---------------------------------------------------------------------------
# PubItem (원본: PubItem — AbstractBasePhoto 상속)
# ---------------------------------------------------------------------------
class PubItem(AbstractBasePhoto):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookstudio_pub_items",
    )
    title = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    fields_data = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Pub Item"
        verbose_name_plural = "Pub Items"

    def __str__(self):
        return f"PubItem {self.id[:8]} ({self.title})"
