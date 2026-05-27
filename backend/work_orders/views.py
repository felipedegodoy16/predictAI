from rest_framework import viewsets, permissions
from .models import WorkOrder, Maintenance, WorkOrderStatus
from .serializers import WorkOrderSerializer, MaintenanceSerializer, WorkOrderStatusSerializer
from .permissions import IsAdminOrRelatedOrReadOnly


class WorkOrderStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """Lista as colunas do Kanban. Read-only — os status são gerenciados pelo admin."""
    queryset = WorkOrderStatus.objects.all()
    serializer_class = WorkOrderStatusSerializer
    permission_classes = [permissions.IsAuthenticated]


class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.select_related('machine', 'opened_by', 'status').all()
    serializer_class = WorkOrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrRelatedOrReadOnly]
    filterset_fields = ['status', 'priority', 'order_type', 'machine']
    search_fields = ['machine__serial_number', 'production_line']
    ordering_fields = ['opening_date', 'status', 'priority']
    ordering = ['-opening_date']

    def perform_create(self, serializer):
        serializer.save(opened_by=self.request.user)


class MaintenanceViewSet(viewsets.ModelViewSet):
    queryset = Maintenance.objects.all()
    serializer_class = MaintenanceSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filterset_fields = ['machine', 'work_order']
    search_fields = ['description', 'solution']
    ordering_fields = ['performed_date']
    ordering = ['-performed_date']
