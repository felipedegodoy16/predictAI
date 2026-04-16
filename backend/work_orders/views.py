from rest_framework import viewsets, permissions
from .models import WorkOrder, WorkOrderStatus, ErrorType
from .serializers import WorkOrderSerializer, WorkOrderStatusSerializer, ErrorTypeSerializer
from .permissions import IsAdminOrRelatedOrReadOnly

class WorkOrderStatusViewSet(viewsets.ModelViewSet):
    queryset = WorkOrderStatus.objects.all()
    serializer_class = WorkOrderStatusSerializer
    
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

class ErrorTypeViewSet(viewsets.ModelViewSet):
    queryset = ErrorType.objects.all()
    serializer_class = ErrorTypeSerializer
    
    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]

class WorkOrderViewSet(viewsets.ModelViewSet):
    queryset = WorkOrder.objects.all()
    serializer_class = WorkOrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrRelatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
