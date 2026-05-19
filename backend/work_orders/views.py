from rest_framework import viewsets, permissions
from .models import WorkOrder, Maintenance
from .serializers import WorkOrderSerializer, MaintenanceSerializer
from .permissions import IsAdminOrRelatedOrReadOnly

class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all()
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
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser] # For now only admins manage maintenances
    filterset_fields = ['machine', 'work_order']
    search_fields = ['description', 'solution']
    ordering_fields = ['performed_date']
    ordering = ['-performed_date']
