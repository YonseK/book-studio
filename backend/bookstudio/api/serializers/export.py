from rest_framework import serializers


class HTMLImportSerializer(serializers.Serializer):
    html = serializers.CharField(help_text="임포트할 HTML 소스")
    edition_id = serializers.CharField(help_text="대상 BookEdition ID")


class HTMLExportSerializer(serializers.Serializer):
    responsive = serializers.BooleanField(default=False, required=False)
