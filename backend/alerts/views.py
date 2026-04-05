from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Alert
from .serializers import AlertSerializer, AlertCreateSerializer, AlertResolveSerializer
from users.permissions import IsAdminOrTechnician


class AlertListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['machine', 'status', 'risk_level', 'alert_type']
    search_fields = ['title', 'message', 'machine__name']
    ordering_fields = ['created_at', 'risk_level', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Alert.objects.select_related('machine', 'sensor', 'resolved_by').all()
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        if start:
            queryset = queryset.filter(created_at__gte=start)
        if end:
            queryset = queryset.filter(created_at__lte=end)
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AlertCreateSerializer
        return AlertSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsAdminOrTechnician()]
        return [IsAuthenticated()]


class AlertDetailView(generics.RetrieveUpdateAPIView):
    queryset = Alert.objects.select_related('machine', 'sensor', 'resolved_by').all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]


class AlertAcknowledgeView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            alert = Alert.objects.get(pk=pk)
        except Alert.DoesNotExist:
            return Response({'detail': 'Alerta nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        if alert.status != Alert.AlertStatus.OPEN:
            return Response({'detail': 'Apenas alertas abertos podem ser reconhecidos.'}, status=status.HTTP_400_BAD_REQUEST)
        alert.status = Alert.AlertStatus.ACKNOWLEDGED
        alert.save()
        return Response(AlertSerializer(alert).data, status=status.HTTP_200_OK)


class AlertResolveView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrTechnician]

    def patch(self, request, pk):
        try:
            alert = Alert.objects.get(pk=pk)
        except Alert.DoesNotExist:
            return Response({'detail': 'Alerta nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        if alert.status == Alert.AlertStatus.RESOLVED:
            return Response({'detail': 'Alerta ja foi resolvido.'}, status=status.HTTP_400_BAD_REQUEST)
        alert.status = Alert.AlertStatus.RESOLVED
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.save()
        return Response(AlertSerializer(alert).data, status=status.HTTP_200_OK)


class OpenAlertsView(generics.ListAPIView):
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-created_at']

    def get_queryset(self):
        return Alert.objects.filter(status=Alert.AlertStatus.OPEN).select_related('machine', 'sensor')


class HighRiskAlertsView(generics.ListAPIView):
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-created_at']

    def get_queryset(self):
        return Alert.objects.filter(
            risk_level=Alert.RiskLevel.HIGH,
            status__in=[Alert.AlertStatus.OPEN, Alert.AlertStatus.ACKNOWLEDGED],
        ).select_related('machine', 'sensor')
