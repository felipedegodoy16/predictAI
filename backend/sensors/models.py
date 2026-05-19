from django.db import models
from machines.models import Machine

class Sensor(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='sensors')
    sensor_type = models.CharField(max_length=80)
    unit = models.CharField(max_length=20)
    description = models.CharField(max_length=150, null=True, blank=True)
    limit_temp = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['machine', 'sensor_type']

    def __str__(self):
        return f'{self.sensor_type} ({self.unit}) - {self.machine.serial_number}'

class SensorReading(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='readings')
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='readings')
    value = models.DecimalField(max_digits=12, decimal_places=4)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.sensor.sensor_type}: {self.value} {self.sensor.unit} @ {self.timestamp}'
