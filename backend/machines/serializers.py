from rest_framework import serializers
from .models import Machine, MachineStatus


class MachineStatusSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    class Meta:
        model = MachineStatus
        fields = ['id', 'status', 'status_display', 'reason', 'timestamp']


class MachineListSerializer(serializers.ModelSerializer):
    current_status = serializers.SerializerMethodField()

    class Meta:
        model = Machine
        fields = [
            'id', 'production_line', 'manufacturer', 'model',
            'serial_number', 'installation_date', 'current_status'
        ]

    def get_current_status(self, obj):
        status = obj.statuses.first()
        if status:
            return MachineStatusSerializer(status).data
        return None


class MachineSerializer(serializers.ModelSerializer):
    statuses = MachineStatusSerializer(many=True, read_only=True)
    current_status = serializers.SerializerMethodField()

    class Meta:
        model = Machine
        fields = [
            'id', 'production_line', 'manufacturer', 'model',
            'serial_number', 'installation_date', 'current_status', 'statuses'
        ]

    def get_current_status(self, obj):
        status = obj.statuses.first()
        if status:
            return MachineStatusSerializer(status).data
        return None


class MachineStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MachineStatus
        fields = ['status', 'reason']
