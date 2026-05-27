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

# Garante que os status do Kanban existem
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
    {"prod": "Linha A", "fab": "Siemens",     "model": "Motor Indução X1", "sn": "MOT-1001"},
    {"prod": "Linha B", "fab": "Atlas Copco", "model": "Compressor GA37",  "sn": "COMP-2002"},
    {"prod": "Linha A", "fab": "Romi",        "model": "Torno CNC",        "sn": "CNC-3003"},
    {"prod": "Linha C", "fab": "Weg",         "model": "Bomba Centrífuga", "sn": "BOM-4004"},
]

machines = []
for m in machines_data:
    obj = Machine.objects.create(
        production_line=m["prod"],
        manufacturer=m["fab"],
        model=m["model"],
        serial_number=m["sn"],
        installation_date=timezone.now().date() - timedelta(days=random.randint(200, 1200))
    )
    MachineStatus.objects.create(machine=obj, status=MachineStatus.Status.ACTIVE, reason="Seed start")
    machines.append(obj)

# ──────────────────────────────────────────────────────────────
# Perfis de comportamento por máquina (variação realista)
# ──────────────────────────────────────────────────────────────
machine_profiles = [
    # Siemens Motor — estável, poucos picos
    {"t_base": (62, 72), "t_peak_chance": 0.015, "t_peak": (82, 96), "v_base": (1.2, 3.0), "v_peak_chance": 0.012, "v_peak": (5.2, 7.8)},
    # Atlas Copco Compressor — roda quente, mais picos de vibração
    {"t_base": (68, 78), "t_peak_chance": 0.025, "t_peak": (81, 93), "v_base": (1.8, 3.8), "v_peak_chance": 0.020, "v_peak": (5.5, 8.5)},
    # Romi Torno CNC — frio e estável
    {"t_base": (55, 70), "t_peak_chance": 0.010, "t_peak": (81, 90), "v_base": (1.0, 2.5), "v_peak_chance": 0.008, "v_peak": (5.1, 6.5)},
    # Weg Bomba Centrífuga — a mais crítica, maior probabilidade de anomalias
    {"t_base": (70, 79), "t_peak_chance": 0.030, "t_peak": (82, 98), "v_base": (2.0, 4.2), "v_peak_chance": 0.028, "v_peak": (5.3, 9.0)},
]

print("Criando Sensores e Leituras (Ultimos 6 meses - leituras horarias)...")
now = timezone.now()
HISTORY_DAYS = 180  # 6 meses

all_sensors = []
for i, machine in enumerate(machines):
    profile = machine_profiles[i]

    temp_sensor = Sensor.objects.create(
        machine=machine,
        sensor_type='Temperatura',
        unit='°C',
        description=f'Sensor Temp {machine.model}',
        limit_temp=80.0
    )
    vib_sensor = Sensor.objects.create(
        machine=machine,
        sensor_type='Vibração',
        unit='mm/s',
        description=f'Sensor Vibração {machine.model}',
        limit_temp=5.0
    )
    all_sensors.append((machine, temp_sensor, vib_sensor, profile))

    readings = []
    for day_offset in range(HISTORY_DAYS, -1, -1):
        for hour in range(0, 24):  # 1 leitura por hora
            record_time = now - timedelta(days=day_offset, hours=hour)

            # Temperatura com tendência sazonal sutil (ligeiramente mais alta no passado)
            season_factor = 1 + 0.05 * (day_offset / HISTORY_DAYS)
            t_val = random.uniform(*profile["t_base"]) * season_factor
            if random.random() > (1 - profile["t_peak_chance"]):
                t_val = random.uniform(*profile["t_peak"])

            readings.append(SensorReading(
                machine=machine,
                sensor=temp_sensor,
                value=round(t_val, 2),
                timestamp=record_time
            ))

            # Vibração com picos esporádicos
            v_val = random.uniform(*profile["v_base"])
            if random.random() > (1 - profile["v_peak_chance"]):
                v_val = random.uniform(*profile["v_peak"])

            readings.append(SensorReading(
                machine=machine,
                sensor=vib_sensor,
                value=round(v_val, 2),
                timestamp=record_time
            ))

    total = len(readings)
    print(f"  -> {machine.model}: {total:,} leituras geradas. Salvando em lotes...")
    batch_size = 2000
    for idx in range(0, total, batch_size):
        SensorReading.objects.bulk_create(readings[idx:idx + batch_size])

print("Criando Alertas e Ordens de Serviço distribuídos no histórico...")
from sensors.views import _auto_create_work_order, _broadcast_notification

for machine, temp_sensor, vib_sensor, _ in all_sensors:
    critical_readings = (
        SensorReading.objects
        .filter(machine=machine, value__gt=5, sensor__sensor_type='Vibração')
        .order_by('?')[:8]
    )
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

print("\n[OK] Seed finalizado com sucesso! 6 meses de historico gerado.")
