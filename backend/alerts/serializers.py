from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    machine_name = serializers.CharField(source='machine.name', read_only=True)
    sensor_name = serializers.CharField(source='sensor.name', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.name', read_only=True)

    class Meta:
        model = Alert
        fields = [
            'id', 'machine', 'machine_name', 'sensor', 'sensor_name',
            'reading', 'alert_type', 'risk_level', 'status',
            'title', 'message', 'recommendation',
            'resolved_by', 'resolved_by_name', 'resolved_at', 'created_at',
        ]
        read_only_fields = ['created_at', 'resolved_by', 'resolved_at']


class AlertCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = [
            'machine', 'sensor', 'alert_type', 'risk_level',
            'title', 'message', 'recommendation',
        ]


class AlertResolveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ['status']

    def validate_status(self, value):
        if value not in (Alert.AlertStatus.RESOLVED, Alert.AlertStatus.ACKNOWLEDGED):
            raise serializers.ValidationError('Status invalido para esta operacao.')
        return value
