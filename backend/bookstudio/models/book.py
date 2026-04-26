from django.conf import settings
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from bookstudio.utils import uuid_key, short_key
from bookstudio import conf


class BookModeEnum(models.TextChoices):
    BOOK = "BOOK", _("Book")
    BOOK_CHAT = "BCHAT", _("Book Chat")
    BOOK_DRIVE = "BDRIVE", _("Book Drive")
    PHOTO_ALBUM = "PHOALBUM", _("Photo Album")
    MY_PAGE = "MYPAGE", _("My Page")
    WEB_SCRAP_BOOK = "WSBOOK", _("Web Scrap Book")
    VIDEO_ALBUM = "VODALBUM", _("Video Album")
    DOC_ALBUM = "DOCALBUM", _("Document Album")
    FILE_ALBUM = "FILEALBUM", _("File Album")


class BookLayoutEnum(models.TextChoices):
    # 원본 BookSize
    BOOK = "BOOK", _("Book (A4 Portrait)")
    MINI_BOOK = "MBOOK", _("Mini Book")
    CD = "CD", _("CD / Square")
    CARD = "CARD", _("Card")
    CINEMA = "CINEMA", _("Cinema")
    BANNER = "BANNER", _("Banner")
    # PPTX 호환 (신규)
    PPTX_WIDE = "PPTX_WIDE", _("PPTX Wide 16:9")
    PPTX_STANDARD = "PPTX_STD", _("PPTX Standard 4:3")
    PPTX_WIDE_PORTRAIT = "PPTX_WP", _("PPTX Wide Portrait 9:16")
    PPTX_STD_PORTRAIT = "PPTX_SP", _("PPTX Standard Portrait 3:4")
    # 추가 프리셋
    A4_LANDSCAPE = "A4_LAND", _("A4 Landscape")
    CUSTOM = "CUSTOM", _("Custom")


class LicenseEnum(models.TextChoices):
    PUBLIC_DOMAIN = "PD", _("Public Domain")
    GPL = "GPL", _("General Public License")
    LGPL = "LGPL", _("Lesser General Public License")
    BSD = "BSD", _("BSD License")
    MPL = "MPL", _("Mozilla Public License")
    APACHE = "APACHE", _("Apache License")
    MIT = "MIT", _("MIT License")
    EPL = "EPL", _("Eclipse Public License")


class PrivacyEnum(models.TextChoices):
    PUBLIC = "PUBLIC", _("Public")
    FRIENDS = "FRIENDS", _("Friends")
    PRIVATE = "PRIVATE", _("Private")


class CollaboratorRoleEnum(models.TextChoices):
    VIEWER = "VIEWER", _("Viewer")
    COMMENTER = "COMMENTER", _("Commenter")
    EDITOR = "EDITOR", _("Editor")
    CONTENT_MANAGER = "CM", _("Content Manager")
    MANAGER = "MANAGER", _("Manager")


# ---------------------------------------------------------------------------
# Book (원본: BookStudio)
# ---------------------------------------------------------------------------
class Book(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=36,
        default=uuid_key,
        unique=True,
        editable=False,
    )
    short_key = models.CharField(
        max_length=36,
        default=short_key,
        unique=True,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookstudio_books",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookstudio_owned_books",
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
    book_mode = models.CharField(
        max_length=20,
        choices=BookModeEnum.choices,
        default=BookModeEnum.BOOK,
    )
    book_layout = models.CharField(
        max_length=20,
        choices=BookLayoutEnum.choices,
        default=BookLayoutEnum.PPTX_WIDE,
    )
    privacy = models.CharField(
        max_length=20,
        choices=PrivacyEnum.choices,
        default=PrivacyEnum.PRIVATE,
    )
    license = models.CharField(
        max_length=20,
        choices=LicenseEnum.choices,
        default=LicenseEnum.PUBLIC_DOMAIN,
    )
    # 커스텀 비율용 (book_layout=CUSTOM 일 때)
    custom_width = models.PositiveIntegerField(null=True, blank=True)
    custom_height = models.PositiveIntegerField(null=True, blank=True)

    # ── 멀티테넌시 (선택적) ──
    tenant = models.ForeignKey(
        conf.TENANT_MODEL or settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookstudio_books_by_tenant",
        null=True,
        blank=True,
        db_index=True,
    )

    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    allow_clone = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self):
        return f"{self.short_key} ({self.book_layout})"

    def mark_as_deleted(self):
        self.deleted = True
        self.save(update_fields=["deleted"])

    def touch(self):
        self.updated_at = timezone.now()
        self.save(update_fields=["updated_at"])

    def get_latest_edition(self):
        return self.editions.filter(latest=True, deleted=False).first()

    def get_latest_title(self):
        edition = self.editions.filter(deleted=False).order_by("-created_at").first()
        return edition.title if edition else ""

    def is_scrap(self):
        return self.book_mode in (
            BookModeEnum.VIDEO_ALBUM,
            BookModeEnum.WEB_SCRAP_BOOK,
            BookModeEnum.PHOTO_ALBUM,
            BookModeEnum.FILE_ALBUM,
        )


# ---------------------------------------------------------------------------
# BookEdition (원본: BookEdition)
# ---------------------------------------------------------------------------
class BookEditionManager(models.Manager):
    def get_latest(self, book=None):
        return self.filter(book=book, latest=True, deleted=False).first()


class BookEdition(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=36,
        default=uuid_key,
        unique=True,
        editable=False,
    )
    book = models.ForeignKey(
        Book,
        related_name="editions",
        on_delete=models.CASCADE,
    )
    clone_from = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="clones",
        on_delete=models.SET_NULL,
    )
    parent = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        related_name="children",
        on_delete=models.SET_NULL,
    )
    title = models.CharField(max_length=240, default="Note")
    description = models.TextField(blank=True)

    is_published = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    version = models.PositiveSmallIntegerField(default=1)
    latest = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    fields_data = models.JSONField(blank=True, null=True)
    deleted = models.BooleanField(default=False)

    objects = BookEditionManager()

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Book Edition"
        verbose_name_plural = "Book Editions"

    def __str__(self):
        return f"{self.book.short_key} v{self.version} (latest={self.latest})"

    def touch(self):
        self.updated_at = timezone.now()
        self.save(update_fields=["updated_at"])
        self.book.touch()

    def set_as_latest(self):
        old = BookEdition.objects.get_latest(book=self.book)
        if old and old.pk != self.pk:
            old.latest = False
            old.save(update_fields=["latest"])
        self.latest = True
        self.save(update_fields=["latest"])

    def latest_version_number(self):
        result = BookEdition.objects.filter(
            book=self.book, is_active=True, deleted=False
        ).aggregate(largest=models.Max("version"))["largest"]
        return max(result or 1, 1)

    def count_pages(self):
        return self.pages.count()

    def get_cover_page(self):
        return self.pages.order_by("order").first()


# ---------------------------------------------------------------------------
# BookCollaborator (원본: BookStudioCollaborator)
# ---------------------------------------------------------------------------
class BookCollaborator(models.Model):
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
        blank=True,
        null=True,
        related_name="bookstudio_collaborations",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="collaborator_set",
    )
    role = models.CharField(
        max_length=20,
        choices=CollaboratorRoleEnum.choices,
        default=CollaboratorRoleEnum.EDITOR,
    )
    invitation_email = models.EmailField(max_length=254, blank=True, null=True)
    accepted = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Book Collaborator"
        verbose_name_plural = "Book Collaborators"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book"],
                condition=models.Q(deleted=False),
                name="unique_active_collaborator",
            )
        ]

    def __str__(self):
        return f"{self.book.short_key} - {self.user} ({self.role})"

    def mark_as_deleted(self):
        self.deleted = True
        self.save(update_fields=["deleted"])
