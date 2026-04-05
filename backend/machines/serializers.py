from rest_framework import serializers
from .models import Machine


class MachineListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = [
            'id', 'name', 'serial_number', 'model', 'manufacturer',
            'location', 'status', 'installation_date', 'created_at',
        ]


class MachineSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = Machine
        fields = [
            'id', 'name', 'serial_number', 'model', 'manufacturer',
            'location', 'description', 'status', 'installation_date',
            'created_by', 'created_by_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class MachineStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ['status']


class MachineApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ['id', 'name', 'api_key']
