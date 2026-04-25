"""출판 워크플로우 서비스.

원본 BookEdition.create_new_version() 로직을 서비스 레이어로 추출.
BookEdition을 받아서 PubBook/PubPage/PubPanel을 생성하고,
새 에디터 버전(BookEdition)을 생성.
"""

from django.db import transaction

from bookstudio.models.book import BookEdition
from bookstudio.models.publishing import PubBook, PubPage, PubPanel, PubDocument
from bookstudio.services.cloning import CloneService
from bookstudio.utils import uuid_key, short_key


class PublishService:

    @staticmethod
    @transaction.atomic
    def publish(edition: BookEdition) -> BookEdition:
        """현재 BookEdition을 출판하고 새 에디터 버전을 생성.

        Returns:
            새로 생성된 (다음 편집용) BookEdition.
        """
        book = edition.book

        # 0) 이미 발행된 Edition인지 확인
        if hasattr(edition, "pub_book"):
            raise ValueError(
                f"BookEdition {edition.pk}은 이미 발행되었습니다. "
                "새 에디션을 생성한 후 발행하세요."
            )

        # 1) 새 에디터 버전 생성
        new_version = edition.latest_version_number() + 1
        new_edition = BookEdition.objects.create(
            book=book,
            parent=edition,
            title=edition.title,
            description=edition.description,
            version=new_version,
            latest=True,
            fields_data=edition.fields_data,
        )

        # 2) PubBook 생성
        parent_pub = PubBook.objects.get_latest(book=book)
        pub_book = PubBook.objects.create(
            book_edition=edition,
            parent=parent_pub,
            privacy=parent_pub.privacy if parent_pub else book.privacy,
            wallpaper=parent_pub.wallpaper if parent_pub else None,
            wallpaper_image=parent_pub.wallpaper_image if parent_pub else None,
            fields_data=edition.fields_data,
        )

        # 3) 페이지 처리
        for page in edition.pages.all():
            # 새 에디터용 페이지 복제
            CloneService.clone_page(page, new_edition, user=page.user)

            # PubPage 생성
            pub_page = PubPage.objects.create(
                pub_book=pub_book,
                page=page,
                order=page.order,
                fields_data=page.fields_data,
            )

            # PubDocument 생성
            try:
                doc = page.document
                PubDocument.objects.create(
                    pub_page=pub_page,
                    document=doc,
                    contents=doc.contents,
                    markdown_text=doc.markdown_text,
                )
            except Exception:
                pass

            # PubPanel 생성
            for panel in page.panels.all():
                # 새 에디터용 패널 복제
                CloneService.clone_panel(panel, new_edition.pages.get(clone_from=page))

                pub_panel = PubPanel.objects.create(
                    pub_page=pub_page,
                    panel=panel,
                    order=panel.order,
                    fields_data=panel.fields_data,
                )

        # 4) 이전 PubBook latest 해제
        if parent_pub:
            parent_pub.latest = False
            parent_pub.save(update_fields=["latest"])

        # 5) 상태 업데이트
        book.is_published = True
        book.save(update_fields=["is_published"])
        edition.is_published = True
        edition.latest = False
        edition.save(update_fields=["is_published", "latest"])

        return new_edition
