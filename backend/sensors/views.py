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


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _detect_alert_type(sensor):
    """Infere o tipo de alerta baseado no sensor_type."""
    from alerts.models import Alert
    t = (sensor.sensor_type or '').lower()
    if 'vibra' in t:
        return Alert.AlertType.VIBRACAO
    if 'press' in t:
        return Alert.AlertType.PRESSAO
    if 'temp' in t:
        return Alert.AlertType.TEMP_ALTA
    return Alert.AlertType.OUTRO


def _detect_criticality(sensor, value, is_low=False):
    """
    Calcula criticidade relativa ao limite:
    """
    from alerts.models import Alert
    if is_low:
        return Alert.Criticality.ALTA

    ratio = float(value) / float(sensor.limit_temp)
    if ratio < 0.90:
        return Alert.Criticality.BAIXA
    if ratio < 1.00:
        return Alert.Criticality.MEDIA
    return Alert.Criticality.ALTA


def _auto_create_work_order(machine, alert):
    """Cria uma WorkOrder preditiva automaticamente para alertas críticos."""
    from work_orders.models import WorkOrder, WorkOrderStatus

    # Pega os status que indicam que a OS está aberta
    open_statuses = WorkOrderStatus.objects.filter(is_closed=False)
    existing_wo = WorkOrder.objects.filter(machine=machine, status__in=open_statuses).first()

    msg = (
        f'OS gerada/atualizada por alerta crítico.\n'
        f'Sensor: {alert.reading.sensor.sensor_type} '
        f'| Valor detectado: {alert.detected_value} {alert.reading.sensor.unit} '
        f'| Limite: {alert.limit_value} {alert.reading.sensor.unit}'
    )

    if existing_wo:
        # Anexa na OS existente
        existing_wo.observation = (existing_wo.observation or "") + "\n\n[Novo Alerta Anexado]\n" + msg
        existing_wo.priority = WorkOrder.Priority.CRITICA
        existing_wo.save()
        _broadcast_os_notification(existing_wo, is_update=True)
    else:
        # Cria uma nova OS
        todo_status = WorkOrderStatus.objects.order_by('order_index').first()
        if not todo_status:
            return  # Sem status cadastrado, não cria OS

        production_line = machine.production_line or 'Auto-gerada'

        wo = WorkOrder.objects.create(
            machine=machine,
            alert=alert,
            order_type=WorkOrder.OrderType.PREDITIVA,
            production_line=production_line,
            priority=WorkOrder.Priority.CRITICA,
            status=todo_status,
            observation=msg,
        )
        _broadcast_os_notification(wo, is_update=False)

def _broadcast_os_notification(work_order, is_update=False):
    """Cria notificações de atualização ou criação de OS."""
    from django.contrib.auth import get_user_model
    from notifications.models import Notification

    User = get_user_model()
    recipients = User.objects.filter(
        is_active=True,
        profile__in=['administrador', 'operador']
    )

    machine_label = f'{work_order.machine.manufacturer} {work_order.machine.model} ({work_order.machine.serial_number})'

    if is_update:
        title = f'OS Atualizada — {machine_label}'
        message = f'Novos alertas críticos anexados à OS-{work_order.id}. Verifique o Kanban.'
        ntype = 'WARNING'
    else:
        title = f'Nova OS Gerada — {machine_label}'
        message = f'Ordem de Serviço preditiva (OS-{work_order.id}) foi aberta devido a anomalias.'
        ntype = 'CRITICAL'

    Notification.objects.bulk_create([
        Notification(
            user=u,
            title=title,
            message=message,
            notification_type=ntype,
        )
        for u in recipients
    ])


def _broadcast_notification(alert):
    """Cria notificações para todos admins/operadores quando um alerta crítico dispara."""
    from django.contrib.auth import get_user_model
    from notifications.models import Notification

    User = get_user_model()
    recipients = User.objects.filter(
        is_active=True,
        profile__in=['administrador', 'operador']
    )

    sensor = alert.reading.sensor
    machine = alert.machine
    machine_label = f'{machine.manufacturer} {machine.model} ({machine.serial_number})'

    crit_map = {'alta': 'CRITICAL', 'media': 'WARNING', 'baixa': 'INFO'}
    ntype = crit_map.get(alert.criticality, 'WARNING')

    title = f'Alerta {alert.get_criticality_display()} — {machine_label}'
    message = (
        f'Sensor: {sensor.sensor_type} ({sensor.unit})\n'
        f'Valor detectado: {alert.detected_value} {sensor.unit}\n'
        f'Limite configurado: {alert.limit_value} {sensor.unit}'
    )

    Notification.objects.bulk_create([
        Notification(
            user=u,
            title=title,
            message=message,
            notification_type=ntype,
        )
        for u in recipients
    ])


# ─── Views ────────────────────────────────────────────────────────────────────

class SensorListCreateView(generics.ListCreateAPIView):
    serializer_class = SensorSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['machine', 'sensor_type', 'is_active']
    search_fields = ['sensor_type', 'description']
    ordering_fields = ['sensor_type']
    ordering = ['sensor_type']

    def get_queryset(self):
        return Sensor.objects.all()


class SensorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [IsAuthenticated]


class SensorReadingListView(generics.ListAPIView):
    serializer_class = SensorReadingSerializer
    permission_classes = [IsAuthenticated]
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
    permission_classes = [AllowAny]  # simulador não autentica

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reading = serializer.save(machine=serializer.validated_data['sensor'].machine)
        self._process_alert(reading)
        output = SensorReadingSerializer(reading)
        return Response(output.data, status=status.HTTP_201_CREATED)

    def _process_alert(self, reading):
        from alerts.models import Alert
        sensor = reading.sensor
        
        is_high = sensor.limit_temp and reading.value > sensor.limit_temp
        is_low = sensor.min_limit is not None and reading.value < sensor.min_limit
        
        if not (is_high or is_low):
            return
            
        criticality = _detect_criticality(sensor, reading.value, is_low=is_low)
        alert = Alert.objects.create(
            reading=reading,
            machine=sensor.machine,
            alert_type=_detect_alert_type(sensor),
            detected_value=reading.value,
            limit_value=sensor.min_limit if is_low else sensor.limit_temp,
            criticality=criticality,
            viewed=False,
        )
        if criticality == Alert.Criticality.ALTA:
            _auto_create_work_order(sensor.machine, alert)
        _broadcast_notification(alert)


class SensorReadingBulkCreateView(APIView):
    permission_classes = [AllowAny]  # simulador não autentica

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
            created_readings.append(reading)

        created = SensorReading.objects.bulk_create(created_readings)

        # Reload from DB so we have PKs and related objects
        ids = [r.id for r in created if r.id]
        created_with_pk = list(
            SensorReading.objects.select_related('sensor', 'sensor__machine')
            .filter(id__in=ids)
        )

        from alerts.models import Alert
        alerts_to_create = []
        auto_wo_alerts = []

        for reading in created_with_pk:
            sensor = reading.sensor
            
            is_high = sensor.limit_temp and reading.value > sensor.limit_temp
            is_low = sensor.min_limit is not None and reading.value < sensor.min_limit
            
            if not (is_high or is_low):
                continue
                
            criticality = _detect_criticality(sensor, reading.value, is_low=is_low)
            alert = Alert(
                reading=reading,
                machine=sensor.machine,
                alert_type=_detect_alert_type(sensor),
                detected_value=reading.value,
                limit_value=sensor.min_limit if is_low else sensor.limit_temp,
                criticality=criticality,
                viewed=False,
            )
            alerts_to_create.append((alert, criticality, sensor.machine))

        created_alerts = []
        for alert_obj, criticality, machine in alerts_to_create:
            alert_obj.save()  # save individually to get PK for FK in WorkOrder
            created_alerts.append(alert_obj)
            if criticality == Alert.Criticality.ALTA:
                auto_wo_alerts.append((machine, alert_obj))

        for machine, alert in auto_wo_alerts:
            _auto_create_work_order(machine, alert)

        # Notificações para todos os alertas gerados
        for alert_obj in created_alerts:
            _broadcast_notification(alert_obj)

        return Response(
            {
                'created': len(created_with_pk),
                'alerts_generated': len(created_alerts),
                'work_orders_created': len(auto_wo_alerts),
            },
            status=status.HTTP_201_CREATED,
        )
