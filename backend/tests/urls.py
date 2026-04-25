from django.http import JsonResponse
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET


@csrf_exempt
@require_GET
def dev_setup(request):
    """개발용: 샘플 북이 없으면 생성, book_id 반환."""
    from bookstudio.models import Book, BookEdition, Page, Panel

    user = request.user
    book = Book.objects.filter(user=user, deleted=False).first()
    edition = None

    if book:
        edition = book.editions.filter(latest=True, deleted=False).first()

    if not book or not edition:
        if not book:
            book = Book.objects.create(user=user, book_layout="PPTX_WIDE")

        edition = BookEdition.objects.create(
            book=book, title="Dev Book", version=1, latest=True,
        )
        page = Page.objects.create(
            user=user, book_edition=edition, order=0,
            background_color="#f5c842",
        )
        Panel.objects.create(
            user=user, page=page, media_type="HL",
            headline="Hello BookStudio", left=340, top=250,
            width=600, height=80, font_size=48, font_bold=True,
            color="#ffffff", text_align="center", order=0,
        )

    return JsonResponse({
        "book_id": str(book.pk),
        "edition_id": str(edition.pk),
        "user": user.username,
    })


urlpatterns = [
    path("api/studio/", include("bookstudio.api.urls")),
    path("api/dev-setup/", dev_setup, name="dev-setup"),
]
