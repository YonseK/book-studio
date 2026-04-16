from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from bookstudio.utils import uuid_key, short_key


class BackgroundTypeEnum(models.TextChoices):
    COLOR = "CLR", _("Background Color")
    WALLPAPER = "WP", _("Wallpaper")
    VIDEO = "VOD", _("Background Video")


class EditTypeEnum(models.TextChoices):
    WYSIWYG = "wysiwyg", _("Wysiwyg")
    MARKDOWN = "markdown", _("Markdown")


class ArrowEnum(models.TextChoices):
    TOP_LEFT = "TL", _("Top Left")
    TOP_RIGHT = "TR", _("Top Right")
    BOTTOM_LEFT = "BL", _("Bottom Left")
    BOTTOM_RIGHT = "BR", _("Bottom Right")


# ---------------------------------------------------------------------------
# Page (원본: PageStudio)
# ---------------------------------------------------------------------------
class Page(models.Model):
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
        related_name="bookstudio_pages",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookstudio_owned_pages",
        blank=True,
        null=True,
    )
    latest_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="bookstudio_edited_pages",
        on_delete=models.SET_NULL,
    )
    book_edition = models.ForeignKey(
        "bookstudio.BookEdition",
        related_name="pages",
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
    short_key = models.CharField(
        max_length=36,
        default=short_key,
        editable=False,
    )

    # 배경
    background_type = models.CharField(
        max_length=20,
        choices=BackgroundTypeEnum.choices,
        default=BackgroundTypeEnum.COLOR,
    )
    wallpaper = models.ForeignKey(
        "bookstudio.Photo",
        blank=True,
        null=True,
        related_name="page_wallpapers",
        on_delete=models.SET_NULL,
    )
    wallpaper_image = models.ForeignKey(
        "bookstudio.WallpaperImage",
        blank=True,
        null=True,
        related_name="page_wallpapers",
        on_delete=models.SET_NULL,
    )
    background_position_x = models.PositiveSmallIntegerField(default=50)
    background_position_y = models.PositiveSmallIntegerField(default=50)
    background_color = models.CharField(max_length=30, default="#ffffff")
    opacity = models.FloatField(default=1.00)

    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0, db_index=True)

    is_active = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)
    prevent_deletion = models.BooleanField(default=False)
    show_page_memo = models.BooleanField(default=True)
    deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    fields_data = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Page"
        verbose_name_plural = "Pages"

    def __str__(self):
        return f"Page {self.short_key} (order={self.order})"

    def mark_as_deleted(self):
        self.deleted = True
        self.save(update_fields=["deleted"])

    def touch(self):
        self.updated_at = timezone.now()
        self.save(update_fields=["updated_at"])
        if self.book_edition:
            self.book_edition.touch()

    def count_panels(self):
        return self.panels.count()


# ---------------------------------------------------------------------------
# Document (원본: DocumentStudio)
# ---------------------------------------------------------------------------
class Document(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=36,
        default=uuid_key,
        unique=True,
        editable=False,
    )
    page = models.OneToOneField(
        Page,
        related_name="document",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookstudio_documents",
        blank=True,
        null=True,
    )
    latest_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="bookstudio_edited_documents",
        on_delete=models.SET_NULL,
    )
    clone_from = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="clones",
        on_delete=models.SET_NULL,
    )
    contents = models.TextField(blank=True)
    markdown_text = models.TextField(blank=True)
    edit_type = models.CharField(
        max_length=20,
        choices=EditTypeEnum.choices,
        default=EditTypeEnum.WYSIWYG,
    )

    is_active = models.BooleanField(default=True)
    fixed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Document"
        verbose_name_plural = "Documents"

    def __str__(self):
        return f"Document for page {self.page.short_key}"

    def touch(self):
        self.updated_at = timezone.now()
        self.save(update_fields=["updated_at"])
        self.page.touch()


# ---------------------------------------------------------------------------
# PageMemo (원본: PageMemo)
# ---------------------------------------------------------------------------
class PageMemo(models.Model):
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
        related_name="bookstudio_page_memos",
    )
    page = models.ForeignKey(
        Page,
        related_name="memos",
        on_delete=models.CASCADE,
    )
    latest_editor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name="bookstudio_edited_memos",
        on_delete=models.SET_NULL,
    )

    text = models.TextField(blank=True)
    theme = models.PositiveSmallIntegerField(default=0)
    arrow = models.CharField(
        max_length=20,
        choices=ArrowEnum.choices,
        blank=True,
        null=True,
    )

    decimal_width = models.FloatField(default=200.00)
    decimal_height = models.FloatField(default=200.00)
    translate_x = models.FloatField(default=0.00)
    translate_y = models.FloatField(default=0.00)

    is_active = models.BooleanField(default=True)
    private = models.BooleanField(default=False)
    is_secret = models.BooleanField(default=False)
    new_memo = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    fields_data = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Page Memo"
        verbose_name_plural = "Page Memos"

    def __str__(self):
        return f"Memo {self.id[:8]} on page {self.page.short_key}"

    def touch(self):
        self.updated_at = timezone.now()
        self.save(update_fields=["updated_at"])


# ---------------------------------------------------------------------------
# PageMemoComment (원본: PageMemoComment)
# ---------------------------------------------------------------------------
class PageMemoComment(models.Model):
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
        related_name="bookstudio_memo_comments",
    )
    page_memo = models.ForeignKey(
        PageMemo,
        related_name="comments",
        on_delete=models.CASCADE,
    )
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Page Memo Comment"
        verbose_name_plural = "Page Memo Comments"

    def __str__(self):
        return f"Comment {self.id[:8]} on memo {self.page_memo_id[:8]}"

    def touch(self):
        self.updated_at = timezone.now()
        self.save(update_fields=["updated_at"])
        self.page_memo.touch()
