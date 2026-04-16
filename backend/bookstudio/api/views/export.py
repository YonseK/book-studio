from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from bookstudio.models.book import BookEdition
from bookstudio.models.page import Page
from bookstudio.models.publishing import PubBook
from bookstudio.api.serializers.export import HTMLImportSerializer, HTMLExportSerializer
from bookstudio.api.serializers.page import PageSerializer
from bookstudio.services.html_import import import_html, HTMLImportError
from bookstudio.services.html_export import export_page_html, export_book_html
from bookstudio.services.pdf_export import export_pub_book_pdf, export_page_pdf, PDFExportError


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def html_import_view(request):
    """외부 HTML → Page/Panel 변환."""
    serializer = HTMLImportSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    edition_id = serializer.validated_data["edition_id"]
    html_string = serializer.validated_data["html"]

    try:
        edition = BookEdition.objects.get(pk=edition_id, book__user=request.user)
    except BookEdition.DoesNotExist:
        return Response(
            {"detail": "에디션을 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        pages = import_html(html_string, edition, request.user)
    except HTMLImportError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    return Response(
        {
            "detail": f"{len(pages)}개 페이지가 생성되었습니다.",
            "pages": PageSerializer(pages, many=True).data,
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def html_export_page_view(request, page_pk):
    """단일 Page → 독립 HTML 내보내기."""
    try:
        page = Page.objects.get(pk=page_pk)
    except Page.DoesNotExist:
        return Response(
            {"detail": "페이지를 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND,
        )

    responsive = request.query_params.get("responsive", "false").lower() == "true"
    html = export_page_html(page, responsive=responsive)

    return Response({"html": html})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def html_export_book_view(request, edition_pk):
    """BookEdition 전체 → HTML 리스트 내보내기."""
    try:
        edition = BookEdition.objects.get(pk=edition_pk, book__user=request.user)
    except BookEdition.DoesNotExist:
        return Response(
            {"detail": "에디션을 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND,
        )

    responsive = request.query_params.get("responsive", "false").lower() == "true"
    pages = export_book_html(edition, responsive=responsive)

    return Response({"pages": pages})


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def pdf_export_page_view(request, page_pk):
    """단일 Page → PDF 내보내기."""
    try:
        page = Page.objects.get(pk=page_pk)
    except Page.DoesNotExist:
        return Response(
            {"detail": "페이지를 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        pdf_bytes = export_page_pdf(page)
    except PDFExportError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    from django.http import HttpResponse

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="page_{page.short_key}.pdf"'
    return response


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def pdf_export_book_view(request, pub_book_pk):
    """PubBook 전체 → PDF 내보내기."""
    try:
        pub_book = PubBook.objects.get(pk=pub_book_pk)
    except PubBook.DoesNotExist:
        return Response(
            {"detail": "출판된 북을 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        pdf_bytes = export_pub_book_pdf(pub_book)
    except PDFExportError as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    from django.http import HttpResponse

    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="book_{pub_book.id[:8]}.pdf"'
    return response
