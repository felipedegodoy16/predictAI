from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'name', 'cpf', 'email', 'username',
            'phone', 'department', 'system_role', 'company_role',
            'password', 'password_confirm',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'As senhas nao conferem.'})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        if not validated_data.get('username'):
            validated_data['username'] = validated_data['email']
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'cpf',
            'system_role', 'company_role', 'department',
            'is_active', 'created_at',
        ]


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'name', 'cpf', 'email', 'username',
            'phone', 'department', 'system_role', 'company_role',
            'is_active', 'last_login', 'created_at', 'updated_at',
        ]
        read_only_fields = ['last_login', 'created_at', 'updated_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'name', 'phone', 'department',
            'system_role', 'company_role', 'is_active',
        ]


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'As senhas nao conferem.'})
        return attrs

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Senha atual incorreta.')
        return value