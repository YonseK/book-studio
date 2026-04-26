from rest_framework import serializers

from bookstudio.models.page import Page, Document, PageMemo, PageMemoComment


class PageSerializer(serializers.ModelSerializer):
    panel_count = serializers.SerializerMethodField()
    has_document = serializers.SerializerMethodField()
    wallpaper = serializers.SerializerMethodField()
    wallpaper_image = serializers.SerializerMethodField()

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

    def get_wallpaper(self, obj):
        fd = obj.fields_data or {}
        if fd.get("wallpaper_url"):
            return fd["wallpaper_url"]
        if obj.wallpaper_id:
            return obj.wallpaper.image_view_url if hasattr(obj.wallpaper, 'image_view_url') else str(obj.wallpaper_id)
        return None

    def get_wallpaper_image(self, obj):
        fd = obj.fields_data or {}
        if fd.get("wallpaper_image_url"):
            return fd["wallpaper_image_url"]
        if obj.wallpaper_image_id:
            return obj.wallpaper_image.image_view_url if hasattr(obj.wallpaper_image, 'image_view_url') else str(obj.wallpaper_image_id)
        return None

    def get_panel_count(self, obj):
        return obj.panels.count()

    def get_has_document(self, obj):
        return hasattr(obj, "document") and obj.document is not None


class PageCreateSerializer(serializers.ModelSerializer):
    book_edition = serializers.PrimaryKeyRelatedField(
        queryset=Page.book_edition.field.related_model.objects.all(),
        required=False,
    )

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
        edition = validated_data.get("book_edition")
        if not edition:
            raise serializers.ValidationError("book_edition is required")
        last_order = edition.pages.order_by("-order").values_list("order", flat=True).first()
        order = (last_order or 0) + 1 if last_order is not None else 0
        return Page.objects.create(user=user, order=order, **validated_data)


class PageUpdateSerializer(serializers.ModelSerializer):
    # FK 필드를 문자열/null 허용으로 오버라이드 (프론트에서 URL 문자열로 전송)
    wallpaper = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    wallpaper_image = serializers.CharField(required=False, allow_null=True, allow_blank=True)

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

    def update(self, instance, validated_data):
        # wallpaper/wallpaper_image: 프론트에서 URL 문자열로 전송됨
        # FK에 저장할 수 없으므로 fields_data에 URL을 보존
        wp = validated_data.pop("wallpaper", None)
        wpi = validated_data.pop("wallpaper_image", None)
        if wp is not None or wpi is not None:
            fd = instance.fields_data or {}
            if wp is not None:
                fd["wallpaper_url"] = wp
            if wpi is not None:
                fd["wallpaper_image_url"] = wpi
            validated_data["fields_data"] = fd
        return super().update(instance, validated_data)


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
