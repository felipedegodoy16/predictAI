from rest_framework import serializers
from .models import WorkOrder, WorkOrderStatus, ErrorType
from users.serializers import UserListSerializer

class WorkOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrderStatus
        fields = '__all__'

class ErrorTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorType
        fields = '__all__'

class WorkOrderSerializer(serializers.ModelSerializer):
    # To return full object representations on GET, but accept IDs on write
    status_detail = WorkOrderStatusSerializer(source='status', read_only=True)
    error_type_detail = ErrorTypeSerializer(source='error_type', read_only=True)

    class Meta:
        model = WorkOrder
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
