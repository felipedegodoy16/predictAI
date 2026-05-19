from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True, default='Sistema')

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'user_name', 'table_name', 'record_id', 'field_name', 'old_value', 'new_value', 'timestamp']
        read_only_fields = fields
