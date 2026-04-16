from rest_framework import serializers

from bookstudio.models.panel import Panel


class PanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Panel
        fields = [
            "id",
            "user",
            "page",
            "media_type",
            # 콘텐츠
            "text",
            "headline",
            "link_url",
            "image",
            "masked_image",
            # 스타일
            "background_color",
            "background_opacity",
            "left",
            "top",
            "width",
            "height",
            "z_index",
            "padding",
            "font_size",
            "font_family",
            "font_style",
            "font_weight",
            "color",
            "text_align",
            "opacity",
            "letter_spacing",
            "line_height",
            "text_decoration",
            "border_width",
            "border_radius",
            "border_color",
            "border_style",
            "border_opacity",
            "stroke_width",
            "text_shadow",
            "box_shadow",
            "image_shadow",
            "text_shadow_px",
            "box_shadow_px",
            "image_shadow_px",
            "drop_shadow_px",
            "angle",
            "translate_x",
            "translate_y",
            "scale_x",
            "scale_y",
            "rotate",
            "font_bold",
            "font_italic",
            "text_underline",
            # 상태
            "order",
            "is_active",
            "fixed",
            "shape_type",
            "created_at",
            "updated_at",
            "fields_data",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class PanelCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Panel
        fields = [
            "page",
            "media_type",
            "text",
            "headline",
            "link_url",
            "image",
            "masked_image",
            # 위치/크기
            "left",
            "top",
            "width",
            "height",
            "z_index",
            # 스타일 (선택)
            "background_color",
            "color",
            "font_size",
            "font_family",
            "opacity",
            "shape_type",
            "fields_data",
        ]

    def create(self, validated_data):
        user = self.context["request"].user
        page = validated_data["page"]
        # order 자동 설정
        last_order = page.panels.order_by("-order").values_list("order", flat=True).first()
        order = (last_order + 1) if last_order is not None else 0
        return Panel.objects.create(user=user, order=order, **validated_data)


class PanelUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Panel
        exclude = ["id", "user", "clone_from", "created_at", "updated_at"]


class PanelSortSerializer(serializers.Serializer):
    """패널 순서 변경용."""

    panel_ids = serializers.ListField(
        child=serializers.CharField(),
        help_text="순서대로 정렬된 패널 ID 리스트",
    )
