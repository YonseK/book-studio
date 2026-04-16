from django.contrib import admin

from bookstudio.models import (
    Book,
    BookEdition,
    BookCollaborator,
    Page,
    Document,
    PageMemo,
    Panel,
    Photo,
    WallpaperImage,
    MediaBank,
    MediaGallery,
    PubItem,
    PubBook,
    PubPage,
    PubPanel,
)


class BookEditionInline(admin.TabularInline):
    model = BookEdition
    extra = 0
    fields = ("id", "title", "version", "latest", "is_published")
    readonly_fields = ("id",)


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("short_key", "user", "book_layout", "book_mode", "is_published", "updated_at")
    list_filter = ("book_layout", "book_mode", "is_published", "deleted")
    search_fields = ("short_key", "user__email")
    inlines = [BookEditionInline]


@admin.register(BookEdition)
class BookEditionAdmin(admin.ModelAdmin):
    list_display = ("id", "book", "title", "version", "latest", "is_published")
    list_filter = ("latest", "is_published")


@admin.register(BookCollaborator)
class BookCollaboratorAdmin(admin.ModelAdmin):
    list_display = ("id", "book", "user", "role", "accepted")
    list_filter = ("role", "accepted")


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ("short_key", "book_edition", "order", "background_type")
    list_filter = ("background_type",)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "page", "edit_type")


@admin.register(PageMemo)
class PageMemoAdmin(admin.ModelAdmin):
    list_display = ("id", "page", "user", "private")


@admin.register(Panel)
class PanelAdmin(admin.ModelAdmin):
    list_display = ("id", "page", "media_type", "order")
    list_filter = ("media_type",)


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "width", "height")


@admin.register(WallpaperImage)
class WallpaperImageAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "wallpaper_layout")
    list_filter = ("wallpaper_layout",)


@admin.register(MediaBank)
class MediaBankAdmin(admin.ModelAdmin):
    list_display = ("id", "book", "bank_type", "title")
    list_filter = ("bank_type",)


@admin.register(MediaGallery)
class MediaGalleryAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title", "is_active")


@admin.register(PubItem)
class PubItemAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "title")


@admin.register(PubBook)
class PubBookAdmin(admin.ModelAdmin):
    list_display = ("id", "book_edition", "latest", "progress_state")
    list_filter = ("latest", "progress_state")


@admin.register(PubPage)
class PubPageAdmin(admin.ModelAdmin):
    list_display = ("id", "pub_book", "order", "transcoded")


@admin.register(PubPanel)
class PubPanelAdmin(admin.ModelAdmin):
    list_display = ("id", "pub_page", "order")
