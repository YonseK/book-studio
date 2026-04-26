from rest_framework import serializers

from bookstudio.models.ai import AISession
from bookstudio.models.design_pattern import (
    DesignPattern,
    DesignPatternSlot,
    DesignPatternSet,
    DesignPatternSetMembership,
)


class DesignPatternSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignPatternSlot
        fields = [
            "id", "role", "media_type",
            "left_pct", "top_pct", "width_pct", "height_pct",
            "style", "order",
        ]


class DesignPatternSerializer(serializers.ModelSerializer):
    slots = DesignPatternSlotSerializer(many=True, read_only=True)
    slot_count = serializers.SerializerMethodField()

    class Meta:
        model = DesignPattern
        fields = [
            "id", "name", "description", "category", "tags",
            "target_layout",
            "page_background_type", "page_background_color", "page_opacity",
            "palette", "typography",
            "source", "source_page",
            "is_active", "usage_count",
            "slots", "slot_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "usage_count", "created_at", "updated_at"]

    def get_slot_count(self, obj):
        # prefetch된 경우 쿼리 없이 계산
        if hasattr(obj, "_prefetched_objects_cache") and "slots" in obj._prefetched_objects_cache:
            return len(obj._prefetched_objects_cache["slots"])
        return obj.slots.count()


class DesignPatternListSerializer(serializers.ModelSerializer):
    """목록용 경량 시리얼라이저 (slots 제외)."""

    slot_count = serializers.SerializerMethodField()

    class Meta:
        model = DesignPattern
        fields = [
            "id", "name", "category", "tags", "target_layout",
            "palette", "source", "is_active", "usage_count", "slot_count",
        ]

    def get_slot_count(self, obj):
        if hasattr(obj, "_prefetched_objects_cache") and "slots" in obj._prefetched_objects_cache:
            return len(obj._prefetched_objects_cache["slots"])
        return obj.slots.count()


class DesignPatternSetSerializer(serializers.ModelSerializer):
    patterns = serializers.SerializerMethodField()

    class Meta:
        model = DesignPatternSet
        fields = [
            "id", "name", "description", "palette",
            "target_layout", "is_active", "patterns", "created_at",
        ]

    def get_patterns(self, obj):
        memberships = obj.memberships.select_related("pattern").order_by("priority")
        return [
            {
                "pattern": DesignPatternListSerializer(m.pattern).data,
                "priority": m.priority,
            }
            for m in memberships
        ]


class DesignPatternSetCreateSerializer(serializers.ModelSerializer):
    pattern_ids = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )

    class Meta:
        model = DesignPatternSet
        fields = ["name", "description", "palette", "target_layout", "pattern_ids"]

    def create(self, validated_data):
        pattern_ids = validated_data.pop("pattern_ids", [])
        pattern_set = DesignPatternSet.objects.create(**validated_data)
        for i, pid in enumerate(pattern_ids):
            DesignPatternSetMembership.objects.create(
                pattern_set=pattern_set, pattern_id=pid, priority=i
            )
        return pattern_set


# ── AISession ──


class AISessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AISession
        fields = [
            "id", "book", "edition", "prompt", "options",
            "status", "error_message",
            "plan", "pattern_set",
            "total_pages", "completed_pages",
            "model_used", "total_input_tokens", "total_output_tokens",
            "created_at", "updated_at", "completed_at",
        ]
        read_only_fields = [
            "id", "status", "error_message", "plan",
            "total_pages", "completed_pages",
            "model_used", "total_input_tokens", "total_output_tokens",
            "created_at", "updated_at", "completed_at",
        ]


class AISessionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AISession
        fields = ["book", "edition", "prompt", "options", "pattern_set"]

    def validate(self, data):
        if str(data["edition"].book_id) != str(data["book"].id):
            raise serializers.ValidationError(
                "Edition does not belong to the book."
            )
        return data
