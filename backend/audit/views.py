from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsAdminOrManager
from .models import AuditLog
from .serializers import AuditLogSerializer

class AuditLogListView(generics.ListAPIView):
    queryset = AuditLog.objects.select_related('user').all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filterset_fields = ['table_name']
    search_fields = ['record_id', 'user__name', 'field_name']
