from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import Sensor, SensorReading
from .serializers import (
    SensorSerializer,
    SensorReadingSerializer,
    SensorReadingCreateSerializer,
    SensorReadingBulkCreateSerializer,
)
from .authentication import MachineApiKeyAuthentication
from users.permissions import IsAdminOrTechnician


class SensorListCreateView(generics.ListCreateAPIView):
    serializer_class = SensorSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTechnician]
    filterset_fields = ['machine', 'sensor_type', 'is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        return Sensor.objects.select_related('machine').all()


class SensorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sensor.objects.select_related('machine').all()
    serializer_class = SensorSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTechnician]


class SensorReadingListView(generics.ListAPIView):
    serializer_class = SensorReadingSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_anomaly']
    ordering_fields = ['timestamp', 'value']
    ordering = ['-timestamp']

    def get_queryset(self):
        sensor_pk = self.kwargs.get('sensor_pk')
        queryset = SensorReading.objects.select_related('sensor').filter(sensor_id=sensor_pk)
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        if start:
            queryset = queryset.filter(timestamp__gte=start)
        if end:
            queryset = queryset.filter(timestamp__lte=end)
        return queryset


class SensorReadingCreateView(generics.CreateAPIView):
    serializer_class = SensorReadingCreateSerializer
    authentication_classes = [MachineApiKeyAuthentication]
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reading = serializer.save()
        if reading.is_anomaly:
            self._create_alert(reading)
        output = SensorReadingSerializer(reading)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def _create_alert(self, reading):
        from alerts.models import Alert
        from alerts.services import get_risk_level, get_recommendation

        risk = get_risk_level(reading.anomaly_score)
        recommendation = get_recommendation(reading.sensor.sensor_type, risk)
        Alert.objects.create(
            machine=reading.sensor.machine,
            sensor=reading.sensor,
            reading=reading,
            alert_type=Alert.AlertType.THRESHOLD,
            risk_level=risk,
            title=f'Anomalia detectada: {reading.sensor.name}',
            message=(
                f'Leitura de {reading.value} {reading.sensor.unit} '
                f'esta fora dos limites definidos (desvio: {reading.anomaly_score}%).'
            ),
            recommendation=recommendation,
        )


class SensorAnomalyListView(generics.ListAPIView):
    serializer_class = SensorReadingSerializer
    permission_classes = [IsAuthenticated]
    ordering = ['-timestamp']

    def get_queryset(self):
        sensor_pk = self.kwargs.get('sensor_pk')
        return SensorReading.objects.filter(sensor_id=sensor_pk, is_anomaly=True).select_related('sensor')


class SensorReadingBulkCreateView(APIView):
    """Endpoint para ingestao de multiplas leituras de sensor em um unico request.

    Autenticado via Machine API Key. Aceita ate 500 leituras por request.
    Gera alertas automaticamente para leituras anomalas.
    """
    authentication_classes = [MachineApiKeyAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SensorReadingBulkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        readings_data = serializer.validated_data['readings']
        created_readings = []
        anomaly_readings = []

        for item in readings_data:
            reading = SensorReading(
                sensor=item['sensor'],
                value=item['value'],
                timestamp=item['timestamp'],
            )
            reading._detect_anomaly()
            created_readings.append(reading)

        SensorReading.objects.bulk_create(created_readings)

        # Generate alerts for anomalies
        anomaly_readings = [r for r in created_readings if r.is_anomaly]
        if anomaly_readings:
            self._create_alerts_bulk(anomaly_readings)

        return Response(
            {
                'created': len(created_readings),
                'anomalies_detected': len(anomaly_readings),
                'alerts_generated': len(anomaly_readings),
            },
            status=status.HTTP_201_CREATED,
        )

    def _create_alerts_bulk(self, anomaly_readings):
        from alerts.models import Alert
        from alerts.services import get_risk_level, get_recommendation

        alerts = []
        for reading in anomaly_readings:
            risk = get_risk_level(reading.anomaly_score)
            recommendation = get_recommendation(reading.sensor.sensor_type, risk)
            alerts.append(Alert(
                machine=reading.sensor.machine,
                sensor=reading.sensor,
                reading=reading,
                alert_type=Alert.AlertType.THRESHOLD,
                risk_level=risk,
                title=f'Anomalia detectada: {reading.sensor.name}',
                message=(
                    f'Leitura de {reading.value} {reading.sensor.unit} '
                    f'esta fora dos limites definidos (desvio: {reading.anomaly_score}%).'
                ),
                recommendation=recommendation,
            ))
        Alert.objects.bulk_create(alerts)
