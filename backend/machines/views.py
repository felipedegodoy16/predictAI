from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Machine, MachineStatus
from .serializers import (
    MachineListSerializer,
    MachineSerializer,
    MachineStatusUpdateSerializer,
)
from .permissions import IsEditorOrReadOnly, IsAdminManagerForDelete


class MachineListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsEditorOrReadOnly]
    search_fields = ['production_line', 'manufacturer', 'model', 'serial_number']
    ordering_fields = ['manufacturer', 'installation_date']
    ordering = ['manufacturer']

    def get_queryset(self):
        return Machine.objects.prefetch_related(
            'statuses',
            'sensors',
            'sensors__readings',
        ).all()

    def perform_create(self, serializer):
        from audit.models import AuditLog
        instance = serializer.save()
        
        # Create initial status
        MachineStatus.objects.create(
            machine=instance,
            status=MachineStatus.Status.ACTIVE,
            reason='Criacao inicial'
        )
        
        AuditLog.objects.create(
            user=self.request.user,
            table_name='MAQUINA',
            record_id=instance.id,
            field_name='NUM_SERIE',
            old_value=None,
            new_value=instance.serial_number
        )

    def get_serializer_class(self):
        return MachineSerializer


class MachineDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Machine.objects.prefetch_related(
        'statuses', 'sensors', 'sensors__readings'
    ).all()
    permission_classes = [IsAuthenticated, IsEditorOrReadOnly, IsAdminManagerForDelete]
    serializer_class = MachineSerializer

    def perform_update(self, serializer):
        from audit.models import AuditLog
        instance = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            table_name='MAQUINA',
            record_id=instance.id,
            field_name='*',
            old_value='--',
            new_value='Atualizado'
        )

    def perform_destroy(self, instance):
        from audit.models import AuditLog
        serial = instance.serial_number
        id_str = instance.id
        instance.delete()
        AuditLog.objects.create(
            user=self.request.user,
            table_name='MAQUINA',
            record_id=id_str,
            field_name='NUM_SERIE',
            old_value=serial,
            new_value='Deletado'
        )


class MachineStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsEditorOrReadOnly]

    def post(self, request, pk):
        try:
            machine = Machine.objects.get(pk=pk)
        except Machine.DoesNotExist:
            return Response({'detail': 'Maquina nao encontrada.'}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = MachineStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(machine=machine)
        
        from audit.models import AuditLog
        AuditLog.objects.create(
            user=request.user,
            table_name='STATUS_MAQUINA',
            record_id=machine.id,
            field_name='STATUS',
            old_value='--',
            new_value=serializer.validated_data['status']
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
