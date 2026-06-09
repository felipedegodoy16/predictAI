from rest_framework import serializers
from .models import Machine, MachineStatus


class MachineStatusSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = MachineStatus
        fields = ['id', 'status', 'status_display', 'reason', 'timestamp']


class SensorSummarySerializer(serializers.Serializer):
    """Leve serializer inline para sensores aninhados na máquina."""
    id = serializers.IntegerField(read_only=True)
    sensor_type = serializers.CharField(read_only=True)
    unit = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    limit_temp = serializers.DecimalField(max_digits=8, decimal_places=2, read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    last_value = serializers.SerializerMethodField()
    last_reading_at = serializers.SerializerMethodField()

    def get_last_value(self, obj):
        reading = obj.readings.first()
        return float(reading.value) if reading else None

    def get_last_reading_at(self, obj):
        reading = obj.readings.first()
        return reading.timestamp if reading else None


class MachineListSerializer(serializers.ModelSerializer):
    current_status = serializers.SerializerMethodField()

    class Meta:
        model = Machine
        fields = [
            'id', 'production_line', 'manufacturer', 'model',
            'serial_number', 'installation_date', 'current_status',
            'telemetry_interval', 'preventive_maintenance_interval',
        ]

    def get_current_status(self, obj):
        s = obj.statuses.first()
        return MachineStatusSerializer(s).data if s else None


class MachineSerializer(serializers.ModelSerializer):
    statuses = MachineStatusSerializer(many=True, read_only=True)
    current_status = serializers.SerializerMethodField()
    sensors = SensorSummarySerializer(many=True, read_only=True)

    class Meta:
        model = Machine
        fields = [
            'id', 'production_line', 'manufacturer', 'model',
            'serial_number', 'installation_date', 'telemetry_interval', 
            'preventive_maintenance_interval',
            'current_status', 'statuses', 'sensors',
        ]

    def get_current_status(self, obj):
        s = obj.statuses.first()
        return MachineStatusSerializer(s).data if s else None


class MachineStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineStatus
        fields = ['status', 'reason']
