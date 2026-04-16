from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from bookstudio.utils import uuid_key
from bookstudio.models.media import WallpaperLayoutEnum


class MediaBankTypeEnum(models.TextChoices):
    WALLPAPER = "WP", _("Wallpaper")
    SPECIAL_EFFECT = "FX", _("Special Effect")
    WIDGET = "WGT", _("Widget")
    IMAGE = "IMG", _("Image")
    VIDEO = "VOD", _("Video")


# ---------------------------------------------------------------------------
# MediaBank (원본: MediaBank)
# ---------------------------------------------------------------------------
class MediaBank(models.Model):
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
        related_name="bookstudio_media_banks",
    )
    book = models.ForeignKey(
        "bookstudio.Book",
        related_name="media_banks",
        on_delete=models.CASCADE,
    )
    clone_from = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="clones",
        on_delete=models.SET_NULL,
    )
    title = models.CharField(max_length=120, blank=True)
    is_sample = models.BooleanField(default=False)

    image = models.ForeignKey(
        "bookstudio.Photo",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    wallpaper_image = models.ForeignKey(
        "bookstudio.WallpaperImage",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    wallpaper_layout = models.CharField(
        max_length=20,
        choices=WallpaperLayoutEnum.choices,
        default=WallpaperLayoutEnum.MINI_BOOK,
    )
    api_name = models.CharField(max_length=240, blank=True)
    bank_type = models.CharField(
        max_length=20,
        choices=MediaBankTypeEnum.choices,
        default=MediaBankTypeEnum.WALLPAPER,
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Media Bank"
        verbose_name_plural = "Media Banks"

    def __str__(self):
        return f"MediaBank {self.id[:8]} ({self.bank_type})"


# ---------------------------------------------------------------------------
# MediaGallery (원본: MediaGallery)
# ---------------------------------------------------------------------------
class MediaGallery(models.Model):
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
        related_name="bookstudio_galleries",
    )
    title = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    sample_is_confirmed = models.BooleanField(default=False)

    image = models.ForeignKey(
        "bookstudio.Photo",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    wallpaper_image = models.ForeignKey(
        "bookstudio.WallpaperImage",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    api_name = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Media Gallery"
        verbose_name_plural = "Media Galleries"

    def __str__(self):
        return f"Gallery {self.id[:8]} ({self.title})"


# ---------------------------------------------------------------------------
# MediaGalleryMembership (원본: MediaGalleryMembership)
# ---------------------------------------------------------------------------
class MediaGalleryMembership(models.Model):
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
        related_name="bookstudio_gallery_memberships",
    )
    name = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Media Gallery Membership"
        verbose_name_plural = "Media Gallery Memberships"

    def __str__(self):
        return f"Membership {self.id[:8]} ({self.name})"


# ---------------------------------------------------------------------------
# MediaGalleryMember (원본: MediaGalleryMember)
# ---------------------------------------------------------------------------
class MediaGalleryMember(models.Model):
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
        related_name="bookstudio_gallery_members",
    )
    membership = models.ForeignKey(
        MediaGalleryMembership,
        related_name="members",
        on_delete=models.CASCADE,
    )
    media_gallery = models.ForeignKey(
        MediaGallery,
        related_name="members",
        on_delete=models.CASCADE,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Media Gallery Member"
        verbose_name_plural = "Media Gallery Members"

    def __str__(self):
        return f"Member {self.id[:8]}"
