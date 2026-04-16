from rest_framework import serializers

from bookstudio.models.page import Page, Document, PageMemo, PageMemoComment


class PageSerializer(serializers.ModelSerializer):
    panel_count = serializers.SerializerMethodField()
    has_document = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = [
            "id",
            "short_key",
            "user",
            "book_edition",
            "order",
            "background_type",
            "wallpaper",
            "wallpaper_image",
            "background_position_x",
            "background_position_y",
            "background_color",
            "opacity",
            "description",
            "is_active",
            "is_locked",
            "prevent_deletion",
            "show_page_memo",
            "created_at",
            "updated_at",
            "fields_data",
            "panel_count",
            "has_document",
        ]
        read_only_fields = ["id", "short_key", "user", "created_at", "updated_at"]

    def get_panel_count(self, obj):
        return obj.panels.count()

    def get_has_document(self, obj):
        return hasattr(obj, "document") and obj.document is not None


class PageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = [
            "book_edition",
            "background_type",
            "wallpaper",
            "wallpaper_image",
            "background_color",
            "opacity",
            "description",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        edition = validated_data["book_edition"]
        # 마지막 order + 1
        last_order = edition.pages.order_by("-order").values_list("order", flat=True).first()
        order = (last_order or 0) + 1 if last_order is not None else 0
        return Page.objects.create(user=user, order=order, **validated_data)


class PageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = [
            "background_type",
            "wallpaper",
            "wallpaper_image",
            "background_position_x",
            "background_position_y",
            "background_color",
            "opacity",
            "description",
            "is_locked",
            "prevent_deletion",
            "show_page_memo",
            "fields_data",
        ]


class PageSortSerializer(serializers.Serializer):
    """페이지 순서 변경용."""

    page_ids = serializers.ListField(
        child=serializers.CharField(),
        help_text="순서대로 정렬된 페이지 ID 리스트",
    )


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id",
            "page",
            "user",
            "contents",
            "markdown_text",
            "edit_type",
            "is_active",
            "fixed",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class DocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["page", "contents", "markdown_text", "edit_type"]

    def create(self, validated_data):
        user = self.context["request"].user
        return Document.objects.create(user=user, **validated_data)


class PageMemoSerializer(serializers.ModelSerializer):
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = PageMemo
        fields = [
            "id",
            "user",
            "page",
            "text",
            "theme",
            "arrow",
            "decimal_width",
            "decimal_height",
            "translate_x",
            "translate_y",
            "is_active",
            "private",
            "is_secret",
            "new_memo",
            "created_at",
            "updated_at",
            "fields_data",
            "comment_count",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def get_comment_count(self, obj):
        return obj.comments.count()


class PageMemoCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageMemoComment
        fields = ["id", "user", "page_memo", "comment", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]
