from rest_framework import serializers
from .models import AuditLog

class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True, default='Sistema')
    action = serializers.SerializerMethodField()
    entity_type = serializers.CharField(source='table_name', read_only=True)
    entity_id = serializers.CharField(source='record_id', read_only=True)
    description = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = ['id', 'user', 'user_name', 'action', 'entity_type', 'entity_id', 'description', 'timestamp']
        read_only_fields = fields

    def get_action(self, obj):
        if obj.new_value == 'Deletado':
            return 'DELETE'
        if obj.old_value is None or obj.old_value == '':
            return 'CREATE'
        if 'LOGIN' in str(obj.new_value).upper() or 'LOGIN' in str(obj.field_name).upper():
            return 'LOGIN'
        return 'UPDATE'

    def get_description(self, obj):
        if obj.new_value == 'Deletado':
            return f"Registro deletado. (Campo antigo: {obj.old_value})"
        if obj.old_value is None or obj.old_value == '':
            return f"Registro criado. (Campo principal: {obj.new_value})"
        return f"Campo '{obj.field_name}' alterado de '{obj.old_value}' para '{obj.new_value}'."
