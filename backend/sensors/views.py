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
    import logging
    logger = logging.getLogger(__name__)

    try:
        from work_orders.models import WorkOrder, WorkOrderStatus

        # Pega o primeiro status "aberto" disponível
        todo_status = WorkOrderStatus.objects.order_by('order_index').first()
        if not todo_status:
            logger.warning("Nenhum WorkOrderStatus cadastrado - OS não foi criada.")
            return

        # Pega os status que indicam que a OS está aberta
        open_statuses = WorkOrderStatus.objects.filter(is_closed=False)
        existing_wo = WorkOrder.objects.filter(machine=machine, status__in=open_statuses).first()

        sensor_label = alert.reading.sensor.sensor_type if alert.reading and alert.reading.sensor else 'desconhecido'
        detected = alert.detected_value
        limit = alert.limit_value
        unit = alert.reading.sensor.unit if alert.reading and alert.reading.sensor else ''

        msg = (
            f'OS gerada automaticamente por alerta crítico.\n'
            f'Sensor: {sensor_label} '
            f'| Valor detectado: {detected} {unit} '
            f'| Limite: {limit} {unit}'
        )

        # production_line: usa da máquina ou fallback genérico
        production_line = (machine.production_line or '').strip() or 'Linha Automática'

        if existing_wo:
            existing_wo.priority = WorkOrder.Priority.CRITICA
            existing_wo.save(update_fields=['priority'])
            logger.info(f"OS-{existing_wo.id} atualizada com novo alerta crítico da máquina {machine.serial_number}.")
            _broadcast_os_notification(existing_wo, is_update=True)
        else:
            import os
            import urllib.request
            import json
            api_key = os.environ.get('GROQ_API_KEY', '')
            ai_text = ""
            if api_key:
                prompt = (
                    f"Crie uma descrição técnica, profissional e 'bem legal' para uma Ordem de Serviço "
                    f"do tipo '{WorkOrder.OrderType.PREDITIVA}'. A máquina envolvida é {machine.manufacturer} {machine.model} "
                    f"(S/N: {machine.serial_number}). "
                    f"O sistema detectou um alerta crítico: Sensor {sensor_label} registrou {detected} {unit} (Limite: {limit} {unit}). "
                    "Gere apenas o texto da descrição a ser colocado na OS, sem aspas, focado na resolução e na clareza."
                )
                try:
                    req = urllib.request.Request(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        },
                        data=json.dumps({
                            "model": "llama3-8b-8192",
                            "messages": [
                                {"role": "system", "content": "Você é um assistente técnico especialista em manutenção industrial preditiva e corretiva."},
                                {"role": "user", "content": prompt}
                            ],
                            "temperature": 0.7,
                            "max_tokens": 512
                        }).encode('utf-8')
                    )
                    with urllib.request.urlopen(req, timeout=10) as response:
                        data = json.loads(response.read().decode('utf-8'))
                        ai_text = data["choices"][0]["message"]["content"].strip()
                except Exception as e:
                    logger.error(f"Erro na API do Groq ao criar OS automatica: {e}")
            
            if ai_text:
                final_obs = f"{msg}\n\n--- Análise IA (Groq) ---\n{ai_text}"
            else:
                final_obs = msg

            wo = WorkOrder.objects.create(
                machine=machine,
                alert=alert,
                order_type=WorkOrder.OrderType.PREDITIVA,
                production_line=production_line,
                priority=WorkOrder.Priority.CRITICA,
                status=todo_status,
                observation=final_obs,
            )
            logger.info(f"OS-{wo.id} criada automaticamente para a máquina {machine.serial_number}.")
            _broadcast_os_notification(wo, is_update=False)

    except Exception as e:
        import traceback
        logger.error(f"Erro ao criar OS automática para máquina {machine.serial_number}: {e}\n{traceback.format_exc()}")

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
        from django.utils import timezone
        from datetime import timedelta

        serializer = SensorReadingBulkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        readings_data = serializer.validated_data['readings']
        created_readings = []
        now = timezone.now()

        for item in readings_data:
            sensor = item['sensor']
            machine = sensor.machine
            interval_mins = machine.telemetry_interval or 0

            if interval_mins > 0:
                latest = SensorReading.objects.filter(sensor=sensor).order_by('-timestamp').first()
                if latest and (now - latest.timestamp) < timedelta(minutes=interval_mins):
                    continue

            reading = SensorReading(
                machine=machine,
                sensor=sensor,
                value=item['value'],
            )
            created_readings.append(reading)

        if not created_readings:
            return Response(
                {
                    'created': 0,
                    'alerts_generated': 0,
                    'work_orders_created': 0,
                    'message': 'All readings ignored due to telemetry interval constraints.'
                },
                status=status.HTTP_200_OK,
            )

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
