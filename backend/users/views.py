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
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ValidateResetCodeSerializer,
    ResetPasswordWithCodeSerializer,
)

from .permissions import IsAdmin, IsAdminOrSelf, IsAdminOrReadOnly


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAdminOrReadOnly]
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
    permission_classes = [IsAuthenticated, IsAdminOrSelf]

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
        if request.user.profile != 'administrador':
            return Response(
                {'detail': 'Apenas administradores podem excluir usuarios.'},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user)
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
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        PasswordResetCode.objects.create(user=user, code=code)
        
        try:
            send_mail(
                subject='Código de Recuperação - PredictAI',
                message=f'Seu código de recuperação de senha é: {code}\nEste código expira em 15 minutos.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response({'detail': 'Código enviado com sucesso.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': 'Erro ao enviar e-mail. Tente novamente mais tarde.', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ValidateResetCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ValidateResetCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        
        user = User.objects.get(email=email)
        time_threshold = timezone.now() - timedelta(minutes=15)
        
        reset_code = PasswordResetCode.objects.filter(user=user, code=code, created_at__gte=time_threshold).first()
        
        if reset_code:
            return Response({'detail': 'Código válido.'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Código inválido ou expirado.'}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordWithCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordWithCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        code = serializer.validated_data['code']
        new_password = serializer.validated_data['new_password']
        
        user = User.objects.get(email=email)
        time_threshold = timezone.now() - timedelta(minutes=15)
        
        reset_code = PasswordResetCode.objects.filter(user=user, code=code, created_at__gte=time_threshold).first()
        
        if reset_code:
            user.set_password(new_password)
            user.save()
            PasswordResetCode.objects.filter(user=user).delete()
            return Response({'detail': 'Senha alterada com sucesso.'}, status=status.HTTP_200_OK)
            
        return Response({'detail': 'Código inválido ou expirado.'}, status=status.HTTP_400_BAD_REQUEST)
