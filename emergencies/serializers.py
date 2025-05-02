from rest_framework import serializers

from .models import EmergencyReport, MissingReport, Report


class EmergencyReportCreateSerializer(serializers.Serializer):
    report_reason = serializers.CharField(max_length=255)
    location = serializers.CharField(max_length=255)


class MissingReportCreateSerializer(serializers.Serializer):
    missing_name = serializers.CharField(max_length=255, required=False)
    missing_health_id = serializers.CharField(max_length=100, required=False)
    description = serializers.CharField()
    last_seen_location = serializers.CharField(max_length=255)
    contact_number = serializers.CharField(max_length=20, required=False)
    photo = serializers.ImageField(required=False)


class EmergencyReportListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyReport
        fields = ['report_reason', 'location']


class MissingReportListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissingReport
        fields = ['missing_name', 'description', 'last_seen_location']


class ReportListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = ['id', 'type', 'status', 'name', 'created_at']

    def get_type(self, obj):
        return obj.get_report_type_display()

    def get_name(self, obj):
        if obj.report_type == 'EMERGENCY' and hasattr(obj, 'emergency_details'):
            return obj.emergency_details.pilgrim.get_full_name()
        elif obj.report_type == 'MISSING' and hasattr(obj, 'missing_details'):
            return obj.missing_details.missing_name
        return None


class ReporterGroupedReportsSerializer(serializers.Serializer):
    reporter_id = serializers.IntegerField()
    reporter_name = serializers.CharField()
    reports = ReportListSerializer(many=True)


