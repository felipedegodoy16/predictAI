from rest_framework import serializers
from .models import Sensor, SensorReading


class SensorSerializer(serializers.ModelSerializer):
    machine_name = serializers.CharField(source='machine.name', read_only=True)

    class Meta:
        model = Sensor
        fields = [
            'id', 'machine', 'machine_name', 'name', 'description',
            'sensor_type', 'unit', 'min_threshold', 'max_threshold',
            'is_active', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class SensorReadingSerializer(serializers.ModelSerializer):
    sensor_name = serializers.CharField(source='sensor.name', read_only=True)
    sensor_unit = serializers.CharField(source='sensor.unit', read_only=True)

    class Meta:
        model = SensorReading
        fields = [
            'id', 'sensor', 'sensor_name', 'sensor_unit',
            'value', 'timestamp', 'is_anomaly', 'anomaly_score', 'created_at',
        ]
        read_only_fields = ['is_anomaly', 'anomaly_score', 'created_at']


class SensorReadingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorReading
        fields = ['sensor', 'value', 'timestamp']

    def validate_sensor(self, sensor):
        if not sensor.is_active:
            raise serializers.ValidationError('Este sensor esta inativo.')
        return sensor


class SensorReadingBulkCreateSerializer(serializers.Serializer):
    """Serializer para ingestao de multiplas leituras em um unico request."""
    readings = SensorReadingCreateSerializer(many=True)

    def validate_readings(self, readings):
        if not readings:
            raise serializers.ValidationError('A lista de leituras nao pode estar vazia.')
        if len(readings) > 500:
            raise serializers.ValidationError(
                'Maximo de 500 leituras por request. Divida em multiplos requests.'
            )
        return readings
