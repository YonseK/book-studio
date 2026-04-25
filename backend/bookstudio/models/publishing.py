from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from bookstudio.utils import uuid_key
from bookstudio.models.book import PrivacyEnum


class ProgressStateEnum(models.TextChoices):
    READY = "READY", _("Ready")
    STARTED = "STARTED", _("Started")
    PENDING = "PENDING", _("Pending")
    SUCCESS = "SUCCESS", _("Success")
    REVOKED = "REVOKED", _("Revoked")
    FAILURE = "FAILURE", _("Failure")


# ---------------------------------------------------------------------------
# PubBook (원본: PubBook)
# ---------------------------------------------------------------------------
class PubBookManager(models.Manager):
    def get_latest(self, book=None):
        if book is None:
            return None
        return self.filter(
            book_edition__book=book, latest=True
        ).first()


class PubBook(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=36,
        default=uuid_key,
        unique=True,
        editable=False,
    )
    book_edition = models.OneToOneField(
        "bookstudio.BookEdition",
        on_delete=models.CASCADE,
        related_name="pub_book",
    )
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )
    privacy = models.CharField(
        max_length=20,
        choices=PrivacyEnum.choices,
        default=PrivacyEnum.PUBLIC,
    )
    is_active = models.BooleanField(default=True)
    latest = models.BooleanField(default=True)

    wallpaper = models.ForeignKey(
        "bookstudio.Photo",
        blank=True,
        null=True,
        related_name="pub_book_wallpapers",
        on_delete=models.SET_NULL,
    )
    wallpaper_image = models.ForeignKey(
        "bookstudio.WallpaperImage",
        blank=True,
        null=True,
        related_name="pub_book_wallpapers",
        on_delete=models.SET_NULL,
    )

    progress_state = models.CharField(
        max_length=20,
        choices=ProgressStateEnum.choices,
        default=ProgressStateEnum.READY,
    )
    fields_data = models.JSONField(blank=True, null=True)

    published_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PubBookManager()

    class Meta:
        ordering = ["-published_at"]
        verbose_name = "Published Book"
        verbose_name_plural = "Published Books"

    def __str__(self):
        return f"PubBook {self.id[:8]} (latest={self.latest})"

    def set_as_latest(self):
        old = PubBook.objects.get_latest(book=self.book_edition.book)
        if old and old.pk != self.pk:
            old.latest = False
            old.save(update_fields=["latest"])
        self.latest = True
        self.save(update_fields=["latest"])

    def get_book_layout(self):
        try:
            return self.book_edition.book.book_layout
        except AttributeError:
            return "PPTX_WIDE"

    def count_pub_pages(self):
        return self.pages.count()

    def get_cover_page(self):
        return self.pages.order_by("order").first()


# ---------------------------------------------------------------------------
# PubPage (원본: PubPage)
# ---------------------------------------------------------------------------
class PubPage(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=36,
        default=uuid_key,
        unique=True,
        editable=False,
    )
    pub_book = models.ForeignKey(
        PubBook,
        related_name="pages",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    page = models.OneToOneField(
        "bookstudio.Page",
        on_delete=models.CASCADE,
        related_name="pub_page",
    )
    order = models.PositiveSmallIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)

    # 렌더링된 HTML (인쇄/변환용)
    page_print_html = models.TextField(blank=True)
    inlinecss_html = models.TextField(blank=True)
    inlinecss_html_thumbnail = models.TextField(blank=True)

    # 페이지 이미지 (HTML→이미지 변환 결과)
    image = models.ForeignKey(
        "bookstudio.Photo",
        blank=True,
        null=True,
        related_name="pub_page_images",
        on_delete=models.SET_NULL,
    )
    transcoded = models.BooleanField(default=False)

    fields_data = models.JSONField(blank=True, null=True)
    published_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["order"]
        verbose_name = "Published Page"
        verbose_name_plural = "Published Pages"

    def __str__(self):
        return f"PubPage {self.id[:8]} (order={self.order})"


# ---------------------------------------------------------------------------
# PubPanel (원본: PubPanel)
# ---------------------------------------------------------------------------
class PubPanel(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=36,
        default=uuid_key,
        unique=True,
        editable=False,
    )
    pub_page = models.ForeignKey(
        PubPage,
        related_name="panels",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    panel = models.OneToOneField(
        "bookstudio.Panel",
        on_delete=models.CASCADE,
        related_name="pub_panel",
    )
    order = models.PositiveSmallIntegerField(default=0, db_index=True)
    is_active = models.BooleanField(default=True)

    fields_data = models.JSONField(blank=True, null=True)
    published_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["order"]
        verbose_name = "Published Panel"
        verbose_name_plural = "Published Panels"

    def __str__(self):
        return f"PubPanel {self.id[:8]} (order={self.order})"


# ---------------------------------------------------------------------------
# PubDocument (원본: PubDocument)
# ---------------------------------------------------------------------------
class PubDocument(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=36,
        default=uuid_key,
        unique=True,
        editable=False,
    )
    pub_page = models.OneToOneField(
        PubPage,
        on_delete=models.CASCADE,
        related_name="document",
    )
    document = models.ForeignKey(
        "bookstudio.Document",
        blank=True,
        null=True,
        related_name="pub_documents",
        on_delete=models.SET_NULL,
    )
    contents = models.TextField(blank=True)
    markdown_text = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Published Document"
        verbose_name_plural = "Published Documents"

    def __str__(self):
        return f"PubDocument for PubPage {self.pub_page_id[:8]}"
