from rest_framework import serializers
from .models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'cnpj', 'email', 'phone',
            'address', 'city', 'state',
            'contact_name', 'contact_email', 'description',
            'is_active', 'created_by', 'created_by_name', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class SupplierListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'cnpj', 'email', 'phone', 'city', 'state', 'is_active']
