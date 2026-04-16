from rest_framework import serializers

from bookstudio.models.media import Photo, WallpaperImage
from bookstudio.models.media_bank import (
    MediaBank,
    MediaGallery,
    MediaGalleryMembership,
    MediaGalleryMember,
)
from bookstudio.models.item_bank import PubItem


# ──────────────────── Photo ────────────────────


class PhotoSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image_view_url = serializers.SerializerMethodField()
    image_thumb_url = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = [
            "id",
            "user",
            "title",
            "image",
            "width",
            "height",
            "size",
            "content_type",
            "image_url",
            "image_view_url",
            "image_thumb_url",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "width",
            "height",
            "size",
            "content_type",
            "created_at",
        ]

    def get_image_url(self, obj):
        return obj.get_image_url()

    def get_image_view_url(self, obj):
        return obj.get_image_view_url()

    def get_image_thumb_url(self, obj):
        return obj.get_image_thumb_url()


class PhotoUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ["image", "title"]

    def create(self, validated_data):
        user = self.context["request"].user
        photo = Photo(user=user, **validated_data)
        photo.save_and_resize()
        return photo


# ──────────────────── WallpaperImage ────────────────────


class WallpaperImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    image_view_url = serializers.SerializerMethodField()
    image_thumb_url = serializers.SerializerMethodField()

    class Meta:
        model = WallpaperImage
        fields = [
            "id",
            "user",
            "title",
            "image",
            "width",
            "height",
            "wallpaper_layout",
            "use_wallpaper",
            "image_url",
            "image_view_url",
            "image_thumb_url",
            "created_at",
        ]
        read_only_fields = ["id", "user", "width", "height", "created_at"]

    def get_image_url(self, obj):
        return obj.get_image_url()

    def get_image_view_url(self, obj):
        layout = obj.wallpaper_layout or "CD"
        return obj.get_layout_image_url(layout, "view") or obj.get_image_url()

    def get_image_thumb_url(self, obj):
        layout = obj.wallpaper_layout or "CD"
        return obj.get_layout_image_url(layout, "thumb") or obj.get_image_url()


class WallpaperImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = WallpaperImage
        fields = ["image", "title", "wallpaper_layout", "use_wallpaper"]

    def create(self, validated_data):
        user = self.context["request"].user
        wp = WallpaperImage(user=user, **validated_data)
        wp.set_image_info()
        wp.save()
        wp.crop_layout()
        wp.save()
        return wp


# ──────────────────── MediaBank ────────────────────


class MediaBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaBank
        fields = [
            "id",
            "user",
            "book",
            "title",
            "is_sample",
            "image",
            "wallpaper_image",
            "wallpaper_layout",
            "api_name",
            "bank_type",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]


class MediaBankCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaBank
        fields = [
            "book",
            "title",
            "image",
            "wallpaper_image",
            "wallpaper_layout",
            "api_name",
            "bank_type",
            "is_sample",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        return MediaBank.objects.create(user=user, **validated_data)


# ──────────────────── MediaGallery ────────────────────


class MediaGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaGallery
        fields = [
            "id",
            "user",
            "title",
            "is_active",
            "sample_is_confirmed",
            "image",
            "wallpaper_image",
            "api_name",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]


# ──────────────────── PubItem ────────────────────


class PubItemSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PubItem
        fields = [
            "id",
            "user",
            "title",
            "image",
            "width",
            "height",
            "is_active",
            "fields_data",
            "image_url",
            "created_at",
        ]
        read_only_fields = ["id", "user", "width", "height", "created_at"]

    def get_image_url(self, obj):
        return obj.get_image_url()


class PubItemUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = PubItem
        fields = ["image", "title", "fields_data"]

    def create(self, validated_data):
        user = self.context["request"].user
        item = PubItem(user=user, **validated_data)
        item.save_and_resize()
        return item
