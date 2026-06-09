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

print("Limpando dados antigos (mantendo Usuarios e Status do Kanban)...")
SensorReading.objects.all().delete()
Alert.objects.all().delete()
WorkOrder.objects.all().delete()
Notification.objects.all().delete()
Sensor.objects.all().delete()
MachineStatus.objects.all().delete()
Machine.objects.all().delete()

# Garante os status do Kanban
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

print("Criando Maquinas...")
machines_data = [
    {"prod": "Linha A", "fab": "Siemens",     "model": "Motor Inducao X1",   "sn": "MOT-1001"},
    {"prod": "Linha B", "fab": "Atlas Copco", "model": "Compressor GA37",    "sn": "COMP-2002"},
    {"prod": "Linha A", "fab": "Romi",        "model": "Torno CNC T15",      "sn": "CNC-3003"},
    {"prod": "Linha C", "fab": "Weg",         "model": "Bomba Centrifuga",   "sn": "BOM-4004"},
    {"prod": "Linha B", "fab": "Bosch",       "model": "Prensa Hidraulica",  "sn": "PRE-5005"},
    {"prod": "Linha C", "fab": "Schneider",   "model": "Inversor de Freq.",  "sn": "INV-6006"},
]

machines = []
for m in machines_data:
    obj = Machine.objects.create(
        production_line=m["prod"],
        manufacturer=m["fab"],
        model=m["model"],
        serial_number=m["sn"],
        installation_date=timezone.now().date() - timedelta(days=random.randint(200, 1500))
    )
    MachineStatus.objects.create(machine=obj, status=MachineStatus.Status.ACTIVE, reason="Seed")
    machines.append(obj)

# ──────────────────────────────────────────────
# Perfis realistas por maquina
# ──────────────────────────────────────────────
machine_profiles = [
    # Siemens Motor — estavel, baixos picos
    {
        "t_base": (60, 70), "t_drift": 0.3,  "t_peak_chance": 0.012, "t_peak": (81, 94),
        "v_base": (1.0, 2.8), "v_peak_chance": 0.010, "v_peak": (5.2, 7.0),
        "c_base": (18, 24),   "c_peak_chance": 0.008, "c_peak": (35, 45),
        "alert_qty": 6,
    },
    # Atlas Copco — quente, vibra mais
    {
        "t_base": (66, 77), "t_drift": 0.5,  "t_peak_chance": 0.022, "t_peak": (82, 95),
        "v_base": (2.0, 4.0), "v_peak_chance": 0.018, "v_peak": (5.5, 9.0),
        "c_base": (22, 30),   "c_peak_chance": 0.015, "c_peak": (38, 50),
        "alert_qty": 10,
    },
    # Romi Torno — frio e estavel
    {
        "t_base": (52, 68), "t_drift": 0.1,  "t_peak_chance": 0.008, "t_peak": (80, 88),
        "v_base": (0.8, 2.2), "v_peak_chance": 0.006, "v_peak": (5.0, 6.5),
        "c_base": (15, 20),   "c_peak_chance": 0.005, "c_peak": (32, 42),
        "alert_qty": 4,
    },
    # Weg Bomba — a mais critica, maior chance de anomalias
    {
        "t_base": (70, 79), "t_drift": 0.8,  "t_peak_chance": 0.030, "t_peak": (82, 99),
        "v_base": (2.5, 4.5), "v_peak_chance": 0.026, "v_peak": (5.4, 10.0),
        "c_base": (25, 35),   "c_peak_chance": 0.022, "c_peak": (40, 55),
        "alert_qty": 14,
    },
    # Bosch Prensa — temperatura media, picos de corrente
    {
        "t_base": (58, 74), "t_drift": 0.4,  "t_peak_chance": 0.018, "t_peak": (81, 92),
        "v_base": (1.5, 3.2), "v_peak_chance": 0.014, "v_peak": (5.1, 7.5),
        "c_base": (20, 28),   "c_peak_chance": 0.020, "c_peak": (36, 52),
        "alert_qty": 9,
    },
    # Schneider Inversor — quente mas vibracao baixa
    {
        "t_base": (65, 76), "t_drift": 0.6,  "t_peak_chance": 0.024, "t_peak": (81, 97),
        "v_base": (0.9, 2.0), "v_peak_chance": 0.007, "v_peak": (5.0, 6.0),
        "c_base": (16, 22),   "c_peak_chance": 0.018, "c_peak": (33, 47),
        "alert_qty": 11,
    },
]

print("Criando Sensores e Leituras (6 meses - a cada 30 min)...")
now = timezone.now()
HISTORY_DAYS = 180

all_sensors = []

for i, machine in enumerate(machines):
    p = machine_profiles[i]

    temp_sensor = Sensor.objects.create(
        machine=machine, sensor_type='Temperatura', unit='grC',
        description=f'Sensor Temperatura {machine.model}', limit_temp=80.0
    )
    vib_sensor = Sensor.objects.create(
        machine=machine, sensor_type='Vibracao', unit='mm/s',
        description=f'Sensor Vibracao {machine.model}', limit_temp=5.0
    )
    corr_sensor = Sensor.objects.create(
        machine=machine, sensor_type='Corrente', unit='A',
        description=f'Sensor Corrente {machine.model}', limit_temp=35.0
    )
    all_sensors.append((machine, temp_sensor, vib_sensor, corr_sensor, p))

    readings = []
    # a cada 30 min = 48 leituras por dia
    for day_offset in range(HISTORY_DAYS, -1, -1):
        # fator sazonal: simula aquecimento progressivo ao longo dos meses
        season = 1.0 + p["t_drift"] * 0.01 * (HISTORY_DAYS - day_offset) / HISTORY_DAYS

        for half_hour in range(0, 48):
            record_time = now - timedelta(days=day_offset, minutes=half_hour * 30)

            # Temperatura com sazonalidade e ruido
            t_val = random.uniform(*p["t_base"]) * season
            t_val += random.gauss(0, 0.8)  # ruido gaussiano
            if random.random() < p["t_peak_chance"]:
                t_val = random.uniform(*p["t_peak"])
            readings.append(SensorReading(machine=machine, sensor=temp_sensor,
                                          value=round(t_val, 2), timestamp=record_time))

            # Vibracao
            v_val = random.uniform(*p["v_base"])
            v_val += random.gauss(0, 0.15)
            if random.random() < p["v_peak_chance"]:
                v_val = random.uniform(*p["v_peak"])
            readings.append(SensorReading(machine=machine, sensor=vib_sensor,
                                          value=round(max(0, v_val), 2), timestamp=record_time))

            # Corrente
            c_val = random.uniform(*p["c_base"])
            c_val += random.gauss(0, 0.5)
            if random.random() < p["c_peak_chance"]:
                c_val = random.uniform(*p["c_peak"])
            readings.append(SensorReading(machine=machine, sensor=corr_sensor,
                                          value=round(max(0, c_val), 2), timestamp=record_time))

    total = len(readings)
    print(f"  [{i+1}/{len(machines)}] {machine.model}: {total:,} leituras. Salvando...")
    for idx in range(0, total, 3000):
        SensorReading.objects.bulk_create(readings[idx:idx + 3000])

print("Criando Alertas e Ordens de Servico...")
from sensors.views import _auto_create_work_order, _broadcast_notification

for machine, temp_sensor, vib_sensor, corr_sensor, p in all_sensors:
    qty = p["alert_qty"]
    critical_vib = (
        SensorReading.objects
        .filter(machine=machine, value__gt=5.0, sensor__sensor_type='Vibracao')
        .order_by('?')[:qty]
    )
    for reading in critical_vib:
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

print("\n[OK] Seed finalizado com sucesso!")
total_readings = SensorReading.objects.count()
total_alerts   = Alert.objects.count()
total_wo       = WorkOrder.objects.count()
print(f"  Leituras: {total_readings:,}")
print(f"  Alertas:  {total_alerts}")
print(f"  OS:       {total_wo}")
