import io
import os

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from bookstudio.utils import uuid_key
from bookstudio import conf


def _upload_to(instance, filename):
    return f"bookstudio/photos/{instance.id[:2]}/{filename}"


def _wallpaper_upload_to(instance, filename):
    return f"bookstudio/wallpapers/{instance.id[:2]}/{filename}"


class UseWallpaperEnum(models.TextChoices):
    BOOK = "BOOK", _("Book")
    COLLECTION = "COLLECTION", _("Collection")
    LIBRARY = "LIBRARY", _("Library")
    DRIVE = "DRIVE", _("Drive")
    BCHAT = "BCHAT", _("Book Chat")
    MYPAGE = "MYPAGE", _("My Page")


class WallpaperLayoutEnum(models.TextChoices):
    BOOK = "BOOK", _("Book")
    MINI_BOOK = "MBOOK", _("Mini Book")
    CD = "CD", _("CD")
    CARD = "CARD", _("Card")
    CINEMA = "CINEMA", _("Cinema")
    BANNER = "BANNER", _("Banner")


# ---------------------------------------------------------------------------
# AbstractBasePhoto (원본: AbstractBasePhoto)
# ---------------------------------------------------------------------------
class AbstractBasePhoto(models.Model):
    """이미지 모델의 공통 베이스. Photo, WallpaperImage, PubItem 등이 상속."""

    id = models.CharField(
        primary_key=True,
        max_length=36,
        default=uuid_key,
        unique=True,
        editable=False,
    )
    content_type = models.CharField(max_length=120, blank=True)
    ext = models.CharField(max_length=12, blank=True)
    org_name = models.CharField(max_length=320, blank=True)

    image = models.ImageField(upload_to=_upload_to, blank=True, null=True)
    size = models.PositiveIntegerField(default=0)
    width = models.PositiveSmallIntegerField(default=0)
    height = models.PositiveSmallIntegerField(default=0)

    image_view = models.ImageField(upload_to=_upload_to, blank=True, null=True)
    image_preview = models.ImageField(upload_to=_upload_to, blank=True, null=True)
    image_thumb = models.ImageField(upload_to=_upload_to, blank=True, null=True)

    description = models.TextField(blank=True)
    extra_data = models.JSONField(blank=True, null=True)

    class Meta:
        abstract = True

    def get_image_url(self):
        return self.image.url if self.image else ""

    def get_image_view_url(self):
        return self.image_view.url if self.image_view else self.get_image_url()

    def get_image_preview_url(self):
        return self.image_preview.url if self.image_preview else self.get_image_url()

    def get_image_thumb_url(self):
        return self.image_thumb.url if self.image_thumb else self.get_image_url()

    def set_image_info(self):
        """이미지 파일에서 메타데이터 추출."""
        if not self.image:
            return
        try:
            from PIL import Image as PILImage

            img = PILImage.open(self.image)
            self.width = img.width
            self.height = img.height
            self.size = self.image.size
            name = self.image.name
            self.ext = os.path.splitext(name)[1].lstrip(".")
        except Exception:
            pass

    def resize_image(self, source_field, target_field, max_width):
        """PIL 기반 이미지 리사이즈. source_field → target_field."""
        if not source_field:
            return
        try:
            from PIL import Image as PILImage

            img = PILImage.open(source_field)
            if img.width <= max_width:
                return

            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), PILImage.LANCZOS)

            buffer = io.BytesIO()
            fmt = img.format or "JPEG"
            img.save(buffer, format=fmt)
            buffer.seek(0)

            from django.core.files.base import ContentFile

            ext = self.ext or "jpg"
            target_field.save(
                f"{self.id}_{max_width}.{ext}",
                ContentFile(buffer.read()),
                save=False,
            )
        except Exception:
            pass

    def save_and_resize(self):
        """원본 이미지 저장 후 뷰/프리뷰/썸네일 생성."""
        self.set_image_info()
        self.resize_image(self.image, self.image_view, conf.IMAGE_MAX_WIDTH)
        self.resize_image(self.image, self.image_preview, conf.IMAGE_PREVIEW_WIDTH)
        self.resize_image(self.image, self.image_thumb, conf.IMAGE_THUMB_WIDTH)
        self.save()


# ---------------------------------------------------------------------------
# Photo (원본: Photo)
# ---------------------------------------------------------------------------
class Photo(AbstractBasePhoto):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookstudio_photos",
    )
    title = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    org_image_url = models.URLField(max_length=500, blank=True)
    masked_image = models.ImageField(upload_to=_upload_to, blank=True, null=True)
    fields_data = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Photo"
        verbose_name_plural = "Photos"

    def __str__(self):
        return f"Photo {self.id[:8]} ({self.title})"


# ---------------------------------------------------------------------------
# WallpaperImage (원본: WallpaperImage)
# ---------------------------------------------------------------------------
from bookstudio.conf import WALLPAPER_PAD_WIDTH

# 크롭 대상 레이아웃별 높이 (PAD_WIDTH=768 기준)
BOOK_LAYOUT_HEIGHTS = {
    "BOOK": 1086,
    "MBOOK": 960,
    "CD": 768,
    "CINEMA": 432,
}

# BookLayoutEnum → 월페이퍼 크롭 레이아웃 매핑
# 프론트엔드에서 사용하는 레이아웃을 가장 가까운 비율의 크롭에 대응
LAYOUT_WALLPAPER_MAP = {
    "BOOK": "BOOK",         # A4 Portrait → BOOK
    "MBOOK": "MBOOK",       # Mini Book → MBOOK
    "CD": "CD",             # Square → CD
    "CINEMA": "CINEMA",     # 16:9 → CINEMA
    "PPTX_WIDE": "CINEMA",  # 16:9 → CINEMA
    "PPTX_STD": "CD",       # 4:3 → CD (가장 가까운 비율)
    "PPTX_WP": "BOOK",      # 9:16 → BOOK (세로형)
    "PPTX_SP": "BOOK",      # 3:4 → BOOK (세로형)
    "A4_LAND": "CINEMA",    # ~1.41:1 → CINEMA (가로형)
    "CARD": "CINEMA",       # ~1.39:1 → CINEMA
    "BANNER": None,         # 가변 높이 → 크롭 안 함
    "CUSTOM": None,         # 사용자 지정 → 크롭 안 함
}


class WallpaperImage(AbstractBasePhoto):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookstudio_wallpapers",
    )
    title = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    org_image_url = models.URLField(max_length=500, blank=True)
    fields_data = models.JSONField(blank=True, null=True)

    # 레이아웃별 크롭 이미지
    mbook_image_view = models.ImageField(
        upload_to=_wallpaper_upload_to, blank=True, null=True
    )
    mbook_image_thumb = models.ImageField(
        upload_to=_wallpaper_upload_to, blank=True, null=True
    )
    cd_image_view = models.ImageField(
        upload_to=_wallpaper_upload_to, blank=True, null=True
    )
    cd_image_thumb = models.ImageField(
        upload_to=_wallpaper_upload_to, blank=True, null=True
    )
    cinema_image_view = models.ImageField(
        upload_to=_wallpaper_upload_to, blank=True, null=True
    )
    cinema_image_thumb = models.ImageField(
        upload_to=_wallpaper_upload_to, blank=True, null=True
    )
    banner_image_view = models.ImageField(
        upload_to=_wallpaper_upload_to, blank=True, null=True
    )
    banner_image_thumb = models.ImageField(
        upload_to=_wallpaper_upload_to, blank=True, null=True
    )

    use_wallpaper = models.CharField(
        max_length=20,
        choices=UseWallpaperEnum.choices,
        default=UseWallpaperEnum.BOOK,
    )
    wallpaper_layout = models.CharField(
        max_length=20,
        choices=WallpaperLayoutEnum.choices,
        default=WallpaperLayoutEnum.BOOK,
    )

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Wallpaper Image"
        verbose_name_plural = "Wallpaper Images"

    def __str__(self):
        return f"Wallpaper {self.id[:8]} ({self.wallpaper_layout})"

    def crop_layout(self, layout=None):
        """레이아웃별 비율로 크롭 및 리사이즈.

        원본 WallpaperImage.crop_layout() 로직을 보존:
        MEDIA_PAD_WIDTH=768 기준으로 각 레이아웃 높이에 맞게 center-crop.
        """
        if not self.image:
            return
        try:
            from PIL import Image as PILImage

            img = PILImage.open(self.image)
        except Exception:
            return

        layouts = [layout] if layout else list(BOOK_LAYOUT_HEIGHTS.keys())

        for lay in layouts:
            target_h = BOOK_LAYOUT_HEIGHTS.get(lay)
            if not target_h:
                continue

            target_w = WALLPAPER_PAD_WIDTH
            self._crop_and_save(img.copy(), target_w, target_h, lay)

    def _crop_and_save(self, img, target_w, target_h, layout_name):
        """이미지를 target 비율로 center-crop 후 view/thumb 저장."""
        from PIL import Image as PILImage
        from django.core.files.base import ContentFile

        src_w, src_h = img.size
        ratio = target_w / target_h

        if src_w / src_h > ratio:
            new_w = int(src_h * ratio)
            offset = (src_w - new_w) // 2
            img = img.crop((offset, 0, offset + new_w, src_h))
        else:
            new_h = int(src_w / ratio)
            offset = (src_h - new_h) // 2
            img = img.crop((0, offset, src_w, offset + new_h))

        view_img = img.resize((target_w, target_h), PILImage.LANCZOS)
        thumb_img = img.resize((target_w // 3, target_h // 3), PILImage.LANCZOS)

        ext = self.ext or "jpg"
        fmt = "JPEG" if ext.lower() in ("jpg", "jpeg") else "PNG"

        for suffix, resized, field_name in [
            ("view", view_img, f"{layout_name.lower()}_image_view"),
            ("thumb", thumb_img, f"{layout_name.lower()}_image_thumb"),
        ]:
            # MBOOK → mbook_image_view, CD → cd_image_view 등
            if layout_name == "BOOK":
                # BOOK 레이아웃은 기본 image_view/image_thumb 사용
                field_name = f"image_{suffix}" if suffix == "thumb" else "image_view"

            field = getattr(self, field_name, None)
            if field is None:
                continue

            buffer = io.BytesIO()
            resized.save(buffer, format=fmt)
            buffer.seek(0)
            field.save(
                f"{self.id}_{layout_name}_{suffix}.{ext}",
                ContentFile(buffer.read()),
                save=False,
            )

    def get_layout_image_url(self, layout, size="view"):
        """레이아웃에 맞는 이미지 URL 반환.

        LAYOUT_WALLPAPER_MAP을 통해 BookLayout을 크롭 레이아웃에 매핑.
        BANNER/CUSTOM 등 매핑이 None인 경우 원본 이미지 반환.
        """
        crop_layout = LAYOUT_WALLPAPER_MAP.get(layout)
        if crop_layout is None:
            return self.get_image_url()
        if crop_layout == "BOOK":
            field_name = "image_view" if size == "view" else "image_thumb"
        else:
            field_name = f"{crop_layout.lower()}_image_{size}"
        field = getattr(self, field_name, None)
        if field:
            return field.url
        return self.get_image_url()
