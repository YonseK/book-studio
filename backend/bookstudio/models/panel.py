from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from bookstudio.utils import uuid_key


class MediaTypeEnum(models.TextChoices):
    TXT = "TXT", _("Text")
    HL = "HL", _("Headline")
    IMG = "IMG", _("Image")
    WS = "WS", _("Web Scraping")
    VOD = "VOD", _("Video")
    AUDIO = "AUDIO", _("Audio")
    EV = "EV", _("Embed Video")
    SHA = "SHA", _("Shape")
    WGT = "WGT", _("Widget")
    PDF = "PDF", _("PDF")
    FILE = "FILE", _("File")
    DOC = "DOC", _("Document")
    PT = "PT", _("Presentation")
    BC = "BC", _("Book Comment")


class MaskedImageEnum(models.TextChoices):
    CIRCLE = "CIRCLE", _("Circle")
    TOP = "TOP", _("Top")
    BOTTOM = "BOTTOM", _("Bottom")
    LEFT = "LEFT", _("Left")
    RIGHT = "RIGHT", _("Right")


# ---------------------------------------------------------------------------
# Panel (원본: PanelStudio = AbstractStyleProperty + PanelCloneMixin + OrderedModel)
# ---------------------------------------------------------------------------
class Panel(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=36,
        default=uuid_key,
        unique=True,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookstudio_panels",
    )
    latest_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="bookstudio_edited_panels",
        on_delete=models.SET_NULL,
    )
    page = models.ForeignKey(
        "bookstudio.Page",
        related_name="panels",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    clone_from = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="clones",
        on_delete=models.SET_NULL,
    )
    media_type = models.CharField(
        max_length=20,
        choices=MediaTypeEnum.choices,
        default=MediaTypeEnum.TXT,
    )

    # 콘텐츠
    text = models.TextField(blank=True)
    headline = models.TextField(blank=True)
    link_url = models.URLField(max_length=240, blank=True)

    # 미디어 FK
    image = models.ForeignKey(
        "bookstudio.Photo",
        blank=True,
        null=True,
        related_name="panels",
        on_delete=models.SET_NULL,
    )
    masked_image = models.CharField(
        max_length=20,
        choices=MaskedImageEnum.choices,
        null=True,
        default=None,
    )

    # --- 스타일 속성 (원본 AbstractStyleProperty) ---
    background_color = models.CharField(max_length=30, default="transparent")
    background_opacity = models.FloatField(default=1.00)

    left = models.SmallIntegerField(default=0)
    top = models.SmallIntegerField(default=0)
    width = models.FloatField(default=300.00)
    height = models.FloatField(default=200.00)
    z_index = models.SmallIntegerField(default=0)
    padding = models.SmallIntegerField(default=0)

    font_size = models.PositiveSmallIntegerField(default=16)
    font_family = models.CharField(max_length=60, default="initial")
    font_style = models.CharField(max_length=30, default="initial")
    font_weight = models.CharField(max_length=30, default="initial")
    color = models.CharField(max_length=30, default="#ffffff")
    text_align = models.CharField(max_length=30, default="initial")
    opacity = models.FloatField(default=1.00)

    letter_spacing = models.FloatField(default=0.00)
    line_height = models.FloatField(default=1.00)
    text_decoration = models.CharField(max_length=30, default="initial")

    border_width = models.PositiveSmallIntegerField(default=0)
    border_radius = models.PositiveSmallIntegerField(default=0)
    border_color = models.CharField(max_length=30, default="#ffffff")
    border_style = models.CharField(max_length=30, default="solid")
    border_opacity = models.FloatField(default=1.00)
    stroke_width = models.FloatField(default=0.0)

    text_shadow = models.CharField(max_length=240, default="initial")
    box_shadow = models.CharField(max_length=240, default="initial")
    image_shadow = models.CharField(max_length=240, default="initial")
    text_shadow_px = models.SmallIntegerField(default=0)
    box_shadow_px = models.SmallIntegerField(default=0)
    image_shadow_px = models.SmallIntegerField(default=0)
    drop_shadow_px = models.SmallIntegerField(default=0)

    angle = models.SmallIntegerField(default=0)
    translate_x = models.FloatField(default=0.00)
    translate_y = models.FloatField(default=0.00)
    scale_x = models.FloatField(default=1.00)
    scale_y = models.FloatField(default=1.00)
    rotate = models.FloatField(default=0.00)

    font_bold = models.BooleanField(default=False)
    font_italic = models.BooleanField(default=False)
    text_underline = models.BooleanField(default=False)

    # --- 순서/상태 ---
    order = models.PositiveSmallIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)
    fixed = models.BooleanField(default=False)
    shape_type = models.PositiveSmallIntegerField(default=0)
    deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    fields_data = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "Panel"
        verbose_name_plural = "Panels"

    def __str__(self):
        return f"Panel {self.id[:8]} ({self.media_type})"

    def mark_as_deleted(self):
        self.deleted = True
        self.save(update_fields=["deleted"])

    def touch(self):
        self.updated_at = timezone.now()
        self.save(update_fields=["updated_at"])
        if self.page:
            self.page.touch()

    def get_book_layout(self):
        try:
            return self.page.book_edition.book.book_layout
        except AttributeError:
            return "PPTX_WIDE"
