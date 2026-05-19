from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Sensor, SensorReading
from .serializers import (
    SensorSerializer,
    SensorReadingSerializer,
    SensorReadingCreateSerializer,
    SensorReadingBulkCreateSerializer,
)

class SensorListCreateView(generics.ListCreateAPIView):
    serializer_class = SensorSerializer
    permission_classes = [AllowAny] # Keeping simple for now
    filterset_fields = ['machine', 'sensor_type', 'is_active']
    search_fields = ['sensor_type', 'description']
    ordering_fields = ['sensor_type']
    ordering = ['sensor_type']

    def get_queryset(self):
        return Sensor.objects.all()


class SensorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [AllowAny]


class SensorReadingListView(generics.ListAPIView):
    serializer_class = SensorReadingSerializer
    permission_classes = [AllowAny]
    ordering_fields = ['timestamp', 'value']
    ordering = ['-timestamp']

    def get_queryset(self):
        sensor_pk = self.kwargs.get('sensor_pk')
        queryset = SensorReading.objects.filter(sensor_id=sensor_pk)
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')
        if start:
            queryset = queryset.filter(timestamp__gte=start)
        if end:
            queryset = queryset.filter(timestamp__lte=end)
        return queryset


class SensorReadingCreateView(generics.CreateAPIView):
    serializer_class = SensorReadingCreateSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reading = serializer.save()
        self._check_and_create_alert(reading)
        output = SensorReadingSerializer(reading)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def _check_and_create_alert(self, reading):
        from alerts.models import Alert
        sensor = reading.sensor
        if sensor.limit_temp and reading.value > sensor.limit_temp:
            Alert.objects.create(
                reading=reading,
                machine=sensor.machine,
                alert_type=Alert.AlertType.TEMP_ALTA,
                detected_value=reading.value,
                limit_value=sensor.limit_temp,
                criticality=Alert.Criticality.ALTA,
                viewed=False
            )


class SensorReadingBulkCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SensorReadingBulkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        readings_data = serializer.validated_data['readings']
        created_readings = []

        for item in readings_data:
            sensor = item['sensor']
            reading = SensorReading(
                machine=sensor.machine,
                sensor=sensor,
                value=item['value'],
            )
            # Cannot set auto_now_add field directly in bulk_create before save, but we will let django handle it
            created_readings.append(reading)

        created = SensorReading.objects.bulk_create(created_readings)

        # Generate alerts
        alerts = []
        from alerts.models import Alert
        for reading in created:
            sensor = reading.sensor
            if sensor.limit_temp and reading.value > sensor.limit_temp:
                alerts.append(Alert(
                    reading=reading,
                    machine=sensor.machine,
                    alert_type=Alert.AlertType.TEMP_ALTA,
                    detected_value=reading.value,
                    limit_value=sensor.limit_temp,
                    criticality=Alert.Criticality.ALTA,
                    viewed=False
                ))
        
        if alerts:
            Alert.objects.bulk_create(alerts)

        return Response(
            {
                'created': len(created),
                'alerts_generated': len(alerts),
            },
            status=status.HTTP_201_CREATED,
        )
