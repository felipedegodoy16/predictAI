from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Machine
from .serializers import (
    MachineListSerializer,
    MachineSerializer,
    MachineStatusUpdateSerializer,
    MachineApiKeySerializer,
)
from .permissions import IsAdminOrTechnicianOrReadOnly, IsAdminForDelete
from users.permissions import IsAdmin


class MachineListCreateView(generics.ListCreateAPIView):
    queryset = Machine.objects.select_related('created_by').all()
    permission_classes = [IsAuthenticated, IsAdminOrTechnicianOrReadOnly]
    filterset_fields = ['status', 'manufacturer', 'location']
    search_fields = ['name', 'serial_number', 'model', 'manufacturer', 'location']
    ordering_fields = ['name', 'status', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MachineSerializer
        return MachineListSerializer


class MachineDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Machine.objects.select_related('created_by').all()
    permission_classes = [IsAuthenticated, IsAdminOrTechnicianOrReadOnly, IsAdminForDelete]

    def get_serializer_class(self):
        return MachineSerializer


class MachineStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrTechnicianOrReadOnly]

    def patch(self, request, pk):
        try:
            machine = Machine.objects.get(pk=pk)
        except Machine.DoesNotExist:
            return Response({'detail': 'Maquina nao encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MachineStatusUpdateSerializer(machine, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class MachineApiKeyView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, pk):
        try:
            machine = Machine.objects.get(pk=pk)
        except Machine.DoesNotExist:
            return Response({'detail': 'Maquina nao encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = MachineApiKeySerializer(machine)
        return Response(serializer.data, status=status.HTTP_200_OK)
