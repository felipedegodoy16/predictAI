from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):
    machine_serial = serializers.CharField(source='machine.serial_number', read_only=True)
    alert_type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    criticality_display = serializers.CharField(source='get_criticality_display', read_only=True)

    class Meta:
        model = Alert
        fields = [
            'id', 'reading', 'machine', 'machine_serial',
            'alert_type', 'alert_type_display',
            'detected_value', 'limit_value',
            'criticality', 'criticality_display',
            'viewed', 'timestamp',
        ]
        read_only_fields = ['timestamp']


class AlertCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = [
            'reading', 'machine', 'alert_type',
            'detected_value', 'limit_value', 'criticality'
        ]


class AlertViewedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ['viewed']
