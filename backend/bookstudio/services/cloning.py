"""북/페이지/패널 복제 서비스.

원본 CloneStudio 유틸리티를 서비스 레이어로 재구현.
django-clone(model_clone) 의존성을 제거하고 순수 Django ORM으로 구현.
"""

from django.db import transaction

from bookstudio.models.book import Book, BookEdition
from bookstudio.models.page import Page, Document, PageMemo, PageMemoComment
from bookstudio.models.panel import Panel
from bookstudio.utils import uuid_key, short_key


class CloneService:

    @staticmethod
    def clone_panel(panel: Panel, target_page: Page, **overrides) -> Panel:
        """패널 복제. 새 Page에 연결."""
        panel_data = {
            field.name: getattr(panel, field.name)
            for field in panel._meta.fields
            if field.name != "id"
        }
        panel_data.update(
            id=uuid_key(),
            page=target_page,
            clone_from=panel,
        )
        panel_data.update(overrides)
        return Panel.objects.create(**panel_data)

    @staticmethod
    def clone_page(page: Page, target_edition: BookEdition, **overrides) -> Page:
        """페이지 및 하위 요소(Document, Memo, Panel) 모두 복제."""
        page_data = {
            field.name: getattr(page, field.name)
            for field in page._meta.fields
            if field.name != "id"
        }
        page_data.update(
            id=uuid_key(),
            short_key=short_key(),
            book_edition=target_edition,
            clone_from=page,
        )
        page_data.update(overrides)
        new_page = Page.objects.create(**page_data)

        # Document 복제
        try:
            doc = page.document
            Document.objects.create(
                page=new_page,
                user=doc.user,
                clone_from=doc,
                contents=doc.contents,
                markdown_text=doc.markdown_text,
                edit_type=doc.edit_type,
            )
        except Page.document.RelatedObjectDoesNotExist:
            pass

        # Memo 복제
        for memo in page.memos.all():
            new_memo = PageMemo.objects.create(
                user=memo.user,
                page=new_page,
                text=memo.text,
                theme=memo.theme,
                arrow=memo.arrow,
                decimal_width=memo.decimal_width,
                decimal_height=memo.decimal_height,
                translate_x=memo.translate_x,
                translate_y=memo.translate_y,
                private=memo.private,
                is_secret=memo.is_secret,
                fields_data=memo.fields_data,
            )
            for comment in memo.comments.all():
                PageMemoComment.objects.create(
                    user=comment.user,
                    page_memo=new_memo,
                    comment=comment.comment,
                )

        # Panel 복제
        for panel in page.panels.all():
            CloneService.clone_panel(panel, new_page)

        return new_page

    @staticmethod
    @transaction.atomic
    def clone_book(book: Book, user, **overrides) -> Book:
        """북 전체 딥 클론: Book → BookEdition → Pages → Panels."""
        book_data = {
            field.name: getattr(book, field.name)
            for field in book._meta.fields
            if field.name not in ("id", "short_key", "is_published", "created_at", "updated_at")
        }
        book_data.update(
            id=uuid_key(),
            short_key=short_key(),
            user=user,
            clone_from=book,
            is_published=False,
        )
        book_data.update(overrides)
        new_book = Book.objects.create(**book_data)

        edition = book.get_latest_edition()
        if not edition:
            return new_book

        new_edition = BookEdition.objects.create(
            book=new_book,
            clone_from=edition,
            title=edition.title,
            description=edition.description,
            version=1,
            latest=True,
            fields_data=edition.fields_data,
        )

        for page in edition.pages.all():
            CloneService.clone_page(page, new_edition, user=user)

        # MediaBank 복제
        from bookstudio.models.media_bank import MediaBank

        for mb in book.media_banks.all():
            MediaBank.objects.create(
                user=user,
                book=new_book,
                clone_from=mb,
                title=mb.title,
                is_sample=mb.is_sample,
                image=mb.image,
                wallpaper_image=mb.wallpaper_image,
                wallpaper_layout=mb.wallpaper_layout,
                api_name=mb.api_name,
                bank_type=mb.bank_type,
            )

        return new_book
