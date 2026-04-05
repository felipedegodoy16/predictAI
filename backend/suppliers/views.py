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


class SupplierDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Supplier.objects.select_related('created_by').all()
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTechnician]
