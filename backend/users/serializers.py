from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    username = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'id', 'name', 'cpf', 'email', 'username',
            'phone', 'department', 'system_role', 'company_role',
            'password', 'password_confirm',
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({'password_confirm': 'As senhas não conferem.'})
        return attrs

    def validate_cpf(self, value):
        cpf = ''.join(filter(str.isdigit, value))
        if len(cpf) != 11:
            raise serializers.ValidationError('CPF deve conter exatamente 11 dígitos.')
        
        # O banco salva com máscara usualmente (ou podemos decidir limpar).
        # Vamos manter a máscara se foi enviada (max 14)
        if User.objects.filter(cpf=value).exists():
            raise serializers.ValidationError('Este CPF já está em uso.')
            
        return value

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


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Usuário com este e-mail não encontrado.')
        return value


class ValidateResetCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Usuário não encontrado.')
        return attrs


class ResetPasswordWithCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'As senhas não conferem.'})
        email = attrs.get('email')
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Usuário não encontrado.')
        return attrs