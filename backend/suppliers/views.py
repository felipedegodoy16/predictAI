from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Supplier
from .serializers import SupplierSerializer, SupplierListSerializer
from users.permissions import IsAdmin, IsAdminOrTechnician


class SupplierListCreateView(generics.ListCreateAPIView):
    queryset = Supplier.objects.select_related('created_by').all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active', 'city', 'state']
    search_fields = ['name', 'cnpj', 'contact_name', 'city']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SupplierSerializer
        return SupplierListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminOrTechnician()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        from audit.models import AuditLog
        instance = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            action=AuditLog.Action.CREATE,
            entity_type='Supplier',
            entity_id=str(instance.id),
            description=f"Fornecedor '{instance.name}' registrado."
        )


class SupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.select_related('created_by').all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTechnician]

    def perform_update(self, serializer):
        from audit.models import AuditLog
        instance = serializer.save()
        AuditLog.objects.create(
            user=self.request.user,
            action=AuditLog.Action.UPDATE,
            entity_type='Supplier',
            entity_id=str(instance.id),
            description=f"Fornecedor '{instance.name}' atualizado."
        )

    def perform_destroy(self, instance):
        from audit.models import AuditLog
        name = instance.name
        id_str = str(instance.id)
        instance.delete()
        AuditLog.objects.create(
            user=self.request.user,
            action=AuditLog.Action.DELETE,
            entity_type='Supplier',
            entity_id=id_str,
            description=f"Fornecedor '{name}' removido."
        )
