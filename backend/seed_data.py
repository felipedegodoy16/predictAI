import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from machines.models import Machine, MachineStatus
from sensors.models import Sensor, SensorReading
from alerts.models import Alert
from work_orders.models import WorkOrder, WorkOrderStatus
from notifications.models import Notification

print("Limpando dados antigos (mantendo Usuários e Status do Kanban)...")
SensorReading.objects.all().delete()
Alert.objects.all().delete()
WorkOrder.objects.all().delete()
Notification.objects.all().delete()
Sensor.objects.all().delete()
MachineStatus.objects.all().delete()
Machine.objects.all().delete()

# Ensure we have Kanban statuses
STATUSES = [
    {"name": "To Do",       "order_index": 0, "is_closed": False},
    {"name": "In Progress", "order_index": 1, "is_closed": False},
    {"name": "Waiting",     "order_index": 2, "is_closed": False},
    {"name": "Done",        "order_index": 3, "is_closed": True},
]
for s in STATUSES:
    WorkOrderStatus.objects.get_or_create(
        name=s["name"],
        defaults={"order_index": s["order_index"], "is_closed": s["is_closed"]}
    )

print("Criando Máquinas...")
machines_data = [
    {"prod": "Linha A", "fab": "Siemens", "model": "Motor Indução X1", "sn": "MOT-1001"},
    {"prod": "Linha B", "fab": "Atlas Copco", "model": "Compressor GA37", "sn": "COMP-2002"},
    {"prod": "Linha A", "fab": "Romi", "model": "Torno CNC", "sn": "CNC-3003"},
    {"prod": "Linha C", "fab": "Weg", "model": "Bomba Centrífuga", "sn": "BOM-4004"},
]

machines = []
for m in machines_data:
    obj = Machine.objects.create(
        production_line=m["prod"],
        manufacturer=m["fab"],
        model=m["model"],
        serial_number=m["sn"],
        installation_date=timezone.now().date() - timedelta(days=random.randint(100, 1000))
    )
    MachineStatus.objects.create(machine=obj, status=MachineStatus.Status.ACTIVE, reason="Seed start")
    machines.append(obj)

print("Criando Sensores e Leituras (Últimos 14 dias)...")
now = timezone.now()

for machine in machines:
    # Sensor 1: Temperatura
    temp_sensor = Sensor.objects.create(
        machine=machine,
        sensor_type='Temperatura',
        unit='°C',
        description=f'Sensor Temp {machine.model}',
        limit_temp=80.0
    )
    
    # Sensor 2: Vibração
    vib_sensor = Sensor.objects.create(
        machine=machine,
        sensor_type='Vibração',
        unit='mm/s',
        description=f'Sensor Vibração {machine.model}',
        limit_temp=5.0
    )

    # Gerar leituras de hora em hora para os últimos 14 dias
    readings = []
    for day_offset in range(14, -1, -1):
        for hour in range(0, 24, 2):  # A cada 2 horas
            record_time = now - timedelta(days=day_offset, hours=hour)
            
            # Temperatura base 65-75. Com picos aleatórios.
            t_val = random.uniform(65.0, 75.0)
            if random.random() > 0.98:  # 2% de chance de pico anômalo
                t_val = random.uniform(81.0, 95.0)

            readings.append(SensorReading(
                machine=machine,
                sensor=temp_sensor,
                value=round(t_val, 2),
                timestamp=record_time
            ))

            # Vibração base 1.5 - 3.5. Com picos.
            v_val = random.uniform(1.5, 3.5)
            if random.random() > 0.98:
                v_val = random.uniform(5.1, 7.5)
                
            readings.append(SensorReading(
                machine=machine,
                sensor=vib_sensor,
                value=round(v_val, 2),
                timestamp=record_time
            ))
            
    SensorReading.objects.bulk_create(readings)

print("Criando Alertas...")
from sensors.views import _auto_create_work_order, _broadcast_notification

# Buscar leituras que ultrapassaram o limite e gerar alertas esparsos
critical_readings = SensorReading.objects.filter(value__gt=5, sensor__sensor_type='Vibração').order_by('?')[:5]
for reading in critical_readings:
    alert = Alert.objects.create(
        reading=reading,
        machine=reading.machine,
        alert_type=Alert.AlertType.VIBRACAO,
        detected_value=reading.value,
        limit_value=reading.sensor.limit_temp,
        criticality=Alert.Criticality.ALTA,
        timestamp=reading.timestamp
    )
    _auto_create_work_order(reading.machine, alert)
    _broadcast_notification(alert)

print("Seed finalizado com sucesso!")
