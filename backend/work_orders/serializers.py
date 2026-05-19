from rest_framework import serializers
from .models import WorkOrder, Maintenance
from users.serializers import UserListSerializer
from machines.serializers import MachineListSerializer

class MaintenanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Maintenance
        fields = '__all__'


class WorkOrderSerializer(serializers.ModelSerializer):
    machine_detail = MachineListSerializer(source='machine', read_only=True)
    opened_by_detail = UserListSerializer(source='opened_by', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    order_type_display = serializers.CharField(source='get_order_type_display', read_only=True)

    class Meta:
        model = WorkOrder
        fields = '__all__'
        read_only_fields = ['id', 'opening_date', 'opened_by']
