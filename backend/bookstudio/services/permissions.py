"""접근 제어 서비스.

북/페이지/패널에 대한 사용자 권한 검증.
"""

from bookstudio.models.book import Book, BookCollaborator, CollaboratorRoleEnum


def can_edit_book(user, book: Book) -> bool:
    """사용자가 북을 편집할 수 있는지 확인."""
    if book.user_id == user.pk:
        return True
    return BookCollaborator.objects.filter(
        book=book,
        user=user,
        deleted=False,
        accepted=True,
        role__in=[
            CollaboratorRoleEnum.EDITOR,
            CollaboratorRoleEnum.CONTENT_MANAGER,
            CollaboratorRoleEnum.MANAGER,
        ],
    ).exists()


def can_view_book(user, book: Book) -> bool:
    """사용자가 북을 열람할 수 있는지 확인."""
    if book.user_id == user.pk:
        return True
    if book.privacy == "PUBLIC":
        return True
    return BookCollaborator.objects.filter(
        book=book,
        user=user,
        deleted=False,
        accepted=True,
    ).exists()


def can_manage_book(user, book: Book) -> bool:
    """사용자가 북을 관리(삭제, 협력자 관리)할 수 있는지 확인."""
    if book.user_id == user.pk:
        return True
    return BookCollaborator.objects.filter(
        book=book,
        user=user,
        deleted=False,
        accepted=True,
        role=CollaboratorRoleEnum.MANAGER,
    ).exists()
