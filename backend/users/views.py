from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User
from .serializers import (
    UserCreateSerializer,
    UserListSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
)
from .permissions import IsAdmin, IsAdminOrSelf


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdmin]
    search_fields = ['name', 'email', 'cpf', 'department']
    filterset_fields = ['system_role', 'company_role', 'is_active']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserListSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrSelf]

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return UserUpdateSerializer
        return UserDetailSerializer

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        if user == request.user:
            return Response(
                {'detail': 'Voce nao pode excluir sua propria conta.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if request.user.system_role != 'ADMIN':
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
