import os
import django
import random
from django.utils import timezone
from datetime import timedelta

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from machines.models import Machine
from sensors.models import Sensor, SensorReading
from work_orders.models import WorkOrder

print("Iniciando população de telemetrias falsas...")

# Limpar leituras antigas
SensorReading.objects.all().delete()

machines = Machine.objects.all()
if not machines:
    print("Nenhuma máquina encontrada. Crie máquinas primeiro.")
    exit()

total_created = 0

for machine in machines:
    sensor_vib, _ = Sensor.objects.get_or_create(machine=machine, sensor_type='vibração', defaults={'unit': 'mm/s'})
    sensor_temp, _ = Sensor.objects.get_or_create(machine=machine, sensor_type='temperatura', defaults={'unit': '°C'})

    # Pegar uma OS ativa se houver
    active_os = WorkOrder.objects.filter(machine=machine).exclude(status__name__icontains='done').first()
    
    start_date = timezone.now() - timedelta(days=3)
    if active_os and active_os.opening_date:
        start_date = active_os.opening_date - timedelta(days=1)
        
    current_time = start_date
    end_time = timezone.now()
    
    readings = []
    
    while current_time < end_time:
        # Vibração
        vib_val = random.uniform(1.0, 3.5)
        if active_os and current_time >= active_os.opening_date:
            vib_val += random.uniform(2.0, 4.0)
            
        r_vib = SensorReading(
            machine=machine,
            sensor=sensor_vib,
            value=round(vib_val, 2)
        )
        # By setting the field after instantiation, bulk_create usually picks it up
        r_vib.timestamp = current_time
        readings.append(r_vib)
        
        # Temperatura
        temp_val = random.uniform(40.0, 55.0)
        if active_os and current_time >= active_os.opening_date:
            temp_val += random.uniform(10.0, 20.0)
            
        r_temp = SensorReading(
            machine=machine,
            sensor=sensor_temp,
            value=round(temp_val, 2)
        )
        r_temp.timestamp = current_time
        readings.append(r_temp)
        
        current_time += timedelta(minutes=30)
        
    if readings:
        for reading in readings:
            reading.save()
            # Force update timestamp because auto_now_add ignores it on .save()
            SensorReading.objects.filter(id=reading.id).update(timestamp=reading.timestamp)
            
        total_created += len(readings)
        print(f"[{machine.serial_number}] Criadas {len(readings)} leituras...")

print(f"População concluída! Total inserido: {total_created}")
