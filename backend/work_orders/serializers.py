from rest_framework import serializers
from .models import WorkOrder, Maintenance, WorkOrderStatus
from users.serializers import UserListSerializer
from machines.serializers import MachineListSerializer


class WorkOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderStatus
        fields = '__all__'


class MaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintenance
        fields = '__all__'


class WorkOrderSerializer(serializers.ModelSerializer):
    machine_detail = MachineListSerializer(source='machine', read_only=True)
    opened_by_detail = UserListSerializer(source='opened_by', read_only=True)
    status_detail = WorkOrderStatusSerializer(source='status', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    order_type_display = serializers.CharField(source='get_order_type_display', read_only=True)
    latest_sensors = serializers.SerializerMethodField()

    class Meta:
        model = WorkOrder
        fields = '__all__'
        read_only_fields = ['id', 'opening_date', 'opened_by']

    def get_latest_sensors(self, obj):
        if not obj.machine:
            return []
        sensors = obj.machine.sensors.filter(is_active=True)
        result = []
        for s in sensors:
            last = s.readings.order_by('-timestamp').first()
            result.append({
                'sensor_type': s.sensor_type,
                'unit': s.unit,
                'value': last.value if last else None
            })
        return result
