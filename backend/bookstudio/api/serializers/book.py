from rest_framework import serializers

from bookstudio.models.book import (
    Book,
    BookEdition,
    BookCollaborator,
    BookLayoutEnum,
    BookModeEnum,
    CollaboratorRoleEnum,
)


class BookSerializer(serializers.ModelSerializer):
    latest_title = serializers.SerializerMethodField()
    edition_count = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            "id",
            "short_key",
            "user",
            "book_mode",
            "book_layout",
            "privacy",
            "license",
            "custom_width",
            "custom_height",
            "is_active",
            "is_published",
            "allow_clone",
            "created_at",
            "updated_at",
            "latest_title",
            "edition_count",
        ]
        read_only_fields = ["id", "short_key", "user", "created_at", "updated_at"]

    def get_latest_title(self, obj):
        return obj.get_latest_title()

    def get_edition_count(self, obj):
        return obj.editions.count()


class BookCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = [
            "book_mode",
            "book_layout",
            "privacy",
            "license",
            "custom_width",
            "custom_height",
        ]

    def validate(self, attrs):
        if attrs.get("book_layout") == BookLayoutEnum.CUSTOM:
            if not attrs.get("custom_width") or not attrs.get("custom_height"):
                raise serializers.ValidationError(
                    "CUSTOM 레이아웃은 custom_width와 custom_height가 필수입니다."
                )
        return attrs

    def create(self, validated_data):
        from bookstudio.models.page import Page

        user = self.context["request"].user
        book = Book.objects.create(user=user, **validated_data)
        # 기본 에디션 + 초기 페이지 자동 생성
        edition = BookEdition.objects.create(book=book, title="Note", version=1, latest=True)
        Page.objects.create(
            book_edition=edition,
            user=user,
            order=0,
            background_type="CLR",
            background_color="#ffffff",
        )
        return book


class BookEditionSerializer(serializers.ModelSerializer):
    page_count = serializers.SerializerMethodField()

    class Meta:
        model = BookEdition
        fields = [
            "id",
            "book",
            "title",
            "description",
            "is_published",
            "is_active",
            "version",
            "latest",
            "created_at",
            "updated_at",
            "published_at",
            "fields_data",
            "page_count",
        ]
        read_only_fields = [
            "id",
            "book",
            "is_published",
            "version",
            "latest",
            "created_at",
            "updated_at",
            "published_at",
        ]

    def get_page_count(self, obj):
        return obj.count_pages()


class BookEditionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookEdition
        fields = ["title", "description", "fields_data"]


class BookCollaboratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCollaborator
        fields = [
            "id",
            "user",
            "book",
            "role",
            "invitation_email",
            "accepted",
            "rejected",
            "deleted",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class BookCollaboratorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCollaborator
        fields = ["user", "invitation_email", "role"]

    def validate(self, attrs):
        if not attrs.get("user") and not attrs.get("invitation_email"):
            raise serializers.ValidationError(
                "user 또는 invitation_email 중 하나는 필수입니다."
            )
        return attrs
