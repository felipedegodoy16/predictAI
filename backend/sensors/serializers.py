from rest_framework import serializers
from .models import Sensor, SensorReading


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = [
            'id', 'machine', 'sensor_type', 'unit',
            'description', 'limit_temp', 'min_limit', 'is_active',
        ]


class SensorReadingSerializer(serializers.ModelSerializer):
    sensor_type = serializers.CharField(source='sensor.sensor_type', read_only=True)
    sensor_unit = serializers.CharField(source='sensor.unit', read_only=True)

    class Meta:
        model = SensorReading
        fields = ['id', 'sensor', 'sensor_type', 'sensor_unit', 'value', 'timestamp']


class SensorReadingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorReading
        fields = ['sensor', 'value']

    def validate_sensor(self, sensor):
        if not sensor.is_active:
            raise serializers.ValidationError('Este sensor está inativo.')
        return sensor


class SensorReadingBulkCreateSerializer(serializers.Serializer):
    """Serializer para ingestão de múltiplas leituras em um único request."""
    readings = SensorReadingCreateSerializer(many=True)

    def validate_readings(self, readings):
        if not readings:
            raise serializers.ValidationError('A lista de leituras não pode estar vazia.')
        if len(readings) > 500:
            raise serializers.ValidationError(
                'Máximo de 500 leituras por request. Divida em múltiplos requests.'
            )
        return readings
