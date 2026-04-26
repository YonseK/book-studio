from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from bookstudio.models.book import BookLayoutEnum
from bookstudio.utils import uuid_key


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------
class PatternCategoryEnum(models.TextChoices):
    TITLE = "TITLE", _("Title Slide")
    SECTION = "SECTION", _("Section Divider")
    CONTENT = "CONTENT", _("Content")
    CONTENT_TWO_COL = "CONTENT_2COL", _("Two Column Content")
    IMAGE = "IMAGE", _("Image Focus")
    IMAGE_TEXT = "IMG_TXT", _("Image + Text")
    DATA = "DATA", _("Data / Key Figures")
    COMPARISON = "COMPARISON", _("Comparison")
    QUOTE = "QUOTE", _("Quote / Highlight")
    CLOSING = "CLOSING", _("Closing / CTA")
    BLANK = "BLANK", _("Blank Canvas")


class SlotRoleEnum(models.TextChoices):
    TITLE = "title", _("Title")
    SUBTITLE = "subtitle", _("Subtitle")
    BODY = "body", _("Body Text")
    IMAGE = "image", _("Image")
    ACCENT = "accent", _("Accent / Decoration")
    ICON = "icon", _("Icon / Shape")
    CAPTION = "caption", _("Caption")
    NUMBER = "number", _("Key Number / Stat")


class PatternSourceEnum(models.TextChoices):
    LEGACY = "LEGACY", _("Extracted from Legacy")
    CURATED = "CURATED", _("Curated")
    AI_GENERATED = "AI_GEN", _("AI Generated")


# ---------------------------------------------------------------------------
# DesignPattern
# ---------------------------------------------------------------------------
class DesignPattern(models.Model):
    """페이지 레이아웃 + 스타일 템플릿."""

    id = models.CharField(
        primary_key=True, max_length=36, default=uuid_key, editable=False
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=20, choices=PatternCategoryEnum.choices
    )
    tags = models.JSONField(default=list, blank=True)

    target_layout = models.CharField(
        max_length=20,
        choices=BookLayoutEnum.choices,
        default=BookLayoutEnum.PPTX_WIDE,
    )

    # ── 페이지 스타일 ──
    page_background_type = models.CharField(max_length=10, default="CLR")
    page_background_color = models.CharField(max_length=30, default="#ffffff")
    page_opacity = models.FloatField(default=1.0)

    # ── 색상 팔레트 ──
    palette = models.JSONField(default=dict, blank=True)

    # ── 타이포그래피 ──
    typography = models.JSONField(default=dict, blank=True)

    # ── 소스 추적 ──
    source = models.CharField(
        max_length=10,
        choices=PatternSourceEnum.choices,
        default=PatternSourceEnum.CURATED,
    )
    source_page = models.ForeignKey(
        "bookstudio.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="extracted_patterns",
    )

    # ── 메타 ──
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["category", "-usage_count"]
        indexes = [
            models.Index(fields=["category", "target_layout", "is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.category})"

    def save(self, **kwargs):
        if not kwargs.get("raw", False):
            self.updated_at = timezone.now()
        super().save(**kwargs)

    def increment_usage(self):
        self.__class__.objects.filter(pk=self.pk).update(
            usage_count=models.F("usage_count") + 1
        )


# ---------------------------------------------------------------------------
# DesignPatternSlot
# ---------------------------------------------------------------------------
class DesignPatternSlot(models.Model):
    """패턴 내 개별 패널 슬롯 (상대 좌표)."""

    id = models.CharField(
        primary_key=True, max_length=36, default=uuid_key, editable=False
    )
    pattern = models.ForeignKey(
        DesignPattern, related_name="slots", on_delete=models.CASCADE
    )
    role = models.CharField(max_length=20, choices=SlotRoleEnum.choices)
    media_type = models.CharField(max_length=20, default="TXT")

    # ── 상대 좌표 (레이아웃 대비 %) ──
    left_pct = models.FloatField()
    top_pct = models.FloatField()
    width_pct = models.FloatField()
    height_pct = models.FloatField()

    # ── 스타일 오버라이드 (Panel 필드 서브셋) ──
    style = models.JSONField(default=dict, blank=True)

    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.pattern.name} / {self.role} ({self.media_type})"

    def to_absolute(self, layout_width: int, layout_height: int) -> dict:
        """상대 좌표를 절대 좌표(px)로 변환."""
        return {
            "left": round(layout_width * self.left_pct / 100),
            "top": round(layout_height * self.top_pct / 100),
            "width": round(layout_width * self.width_pct / 100),
            "height": round(layout_height * self.height_pct / 100),
        }


# ---------------------------------------------------------------------------
# DesignPatternSet
# ---------------------------------------------------------------------------
class DesignPatternSet(models.Model):
    """여러 패턴을 하나의 테마로 묶음."""

    id = models.CharField(
        primary_key=True, max_length=36, default=uuid_key, editable=False
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    palette = models.JSONField(default=dict, blank=True)
    target_layout = models.CharField(
        max_length=20, choices=BookLayoutEnum.choices, default=BookLayoutEnum.PPTX_WIDE
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_pattern(self, category: str):
        """카테고리로 패턴 조회. priority 높은 것 우선."""
        membership = (
            self.memberships.filter(
                pattern__category=category, pattern__is_active=True
            )
            .order_by("priority")
            .select_related("pattern")
            .first()
        )
        return membership.pattern if membership else None

    def get_patterns_by_category(self) -> dict:
        """카테고리별 패턴 목록 반환."""
        result: dict[str, list] = {}
        for m in self.memberships.select_related("pattern").order_by("priority"):
            result.setdefault(m.pattern.category, []).append(m.pattern)
        return result


class DesignPatternSetMembership(models.Model):
    """패턴세트 <-> 패턴 연결 + 우선순위."""

    id = models.CharField(
        primary_key=True, max_length=36, default=uuid_key, editable=False
    )
    pattern_set = models.ForeignKey(
        DesignPatternSet, related_name="memberships", on_delete=models.CASCADE
    )
    pattern = models.ForeignKey(
        DesignPattern, related_name="set_memberships", on_delete=models.CASCADE
    )
    priority = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = [("pattern_set", "pattern")]
        ordering = ["priority"]

    def __str__(self):
        return f"{self.pattern_set.name} / {self.pattern.name} (p={self.priority})"
