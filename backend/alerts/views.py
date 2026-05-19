from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Alert
from .serializers import AlertSerializer, AlertCreateSerializer, AlertViewedSerializer


class AlertListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filterset_fields = ['machine', 'criticality', 'alert_type', 'viewed']
    search_fields = ['machine__serial_number']
    ordering_fields = ['timestamp', 'criticality']
    ordering = ['-timestamp']

    def get_queryset(self):
        queryset = Alert.objects.select_related('machine', 'reading').all()
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        if start:
            queryset = queryset.filter(timestamp__gte=start)
        if end:
            queryset = queryset.filter(timestamp__lte=end)
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AlertCreateSerializer
        return AlertSerializer


class AlertDetailView(generics.RetrieveUpdateAPIView):
    queryset = Alert.objects.select_related('machine', 'reading').all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]


class AlertMarkViewedView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            alert = Alert.objects.get(pk=pk)
        except Alert.DoesNotExist:
            return Response({'detail': 'Alerta nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = AlertViewedSerializer(alert, data={'viewed': True}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(AlertSerializer(alert).data, status=status.HTTP_200_OK)


class UnviewedAlertsView(generics.ListAPIView):
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-timestamp']

    def get_queryset(self):
        return Alert.objects.filter(viewed=False).select_related('machine', 'reading')


class HighRiskAlertsView(generics.ListAPIView):
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-timestamp']

    def get_queryset(self):
        return Alert.objects.filter(
            criticality=Alert.Criticality.ALTA,
            viewed=False,
        ).select_related('machine', 'reading')
