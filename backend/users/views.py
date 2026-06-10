from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import User, PasswordResetCode
from .serializers import (
    UserCreateSerializer,
    UserListSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    MeUpdateSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
)

from .permissions import IsAdminOrManager


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAdminOrManager]
    search_fields = ['name', 'email']
    filterset_fields = ['profile', 'is_active']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserListSerializer

    def perform_create(self, serializer):
        from audit.models import AuditLog
        instance = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            table_name='USUARIO',
            record_id=instance.id,
            field_name='NOME',
            old_value=None,
            new_value=instance.name
        )


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAdminOrManager]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return UserUpdateSerializer
        return UserDetailSerializer

    def perform_update(self, serializer):
        from audit.models import AuditLog
        instance = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            table_name='USUARIO',
            record_id=instance.id,
            field_name='NOME',
            old_value='',
            new_value=instance.name
        )

    def perform_destroy(self, instance):
        from audit.models import AuditLog
        email = instance.email
        id_val = instance.id
        instance.delete()
        AuditLog.objects.create(
            user=self.request.user,
            table_name='USUARIO',
            record_id=id_val,
            field_name='EMAIL',
            old_value=email,
            new_value='Deletado'
        )

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            return Response(
                {'detail': 'Voce nao pode excluir sua propria conta.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.user.profile not in ['administrador', 'gerente']:
            return Response(
                {'detail': 'Apenas administradores e gerentes podem excluir usuarios.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = MeUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'detail': 'Senha alterada com sucesso.'}, status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        
        user = User.objects.get(email=email)
        
        # Gerar uma nova senha aleatória (8 caracteres com letras e números)
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        user.set_password(new_password)
        user.save()
        
        try:
            send_mail(
                subject='Nova Senha - PredictAI',
                message=f'Sua nova senha de acesso é: {new_password}\n\nRecomendamos que você altere esta senha no seu perfil logo após fazer o login.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response({'detail': 'Uma nova senha foi enviada com sucesso para o seu e-mail.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': 'Erro ao enviar e-mail. Tente novamente mais tarde.', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

