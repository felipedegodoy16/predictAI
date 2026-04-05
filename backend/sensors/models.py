from django.db import models
from machines.models import Machine


class Sensor(models.Model):
    class SensorType(models.TextChoices):
        TEMPERATURE = 'TEMPERATURE', 'Temperatura'
        VIBRATION = 'VIBRATION', 'Vibracao'
        PRESSURE = 'PRESSURE', 'Pressao'
        HUMIDITY = 'HUMIDITY', 'Umidade'
        CURRENT = 'CURRENT', 'Corrente Eletrica'
        VOLTAGE = 'VOLTAGE', 'Tensao'
        RPM = 'RPM', 'Rotacao (RPM)'
        OTHER = 'OTHER', 'Outro'

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='sensors')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    sensor_type = models.CharField(max_length=20, choices=SensorType.choices, default=SensorType.OTHER)
    unit = models.CharField(max_length=20)
    min_threshold = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    max_threshold = models.DecimalField(max_digits=12, decimal_places=4, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['machine', 'name']

    def __str__(self):
        return f'{self.name} ({self.sensor_type}) - {self.machine.name}'


class SensorReading(models.Model):
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='readings')
    value = models.DecimalField(max_digits=14, decimal_places=4)
    timestamp = models.DateTimeField()
    is_anomaly = models.BooleanField(default=False)
    anomaly_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['sensor', '-timestamp']),
            models.Index(fields=['is_anomaly', '-timestamp']),
        ]

    def save(self, *args, **kwargs):
        self._detect_anomaly()
        super().save(*args, **kwargs)

    def _detect_anomaly(self):
        sensor = self.sensor
        value = float(self.value)
        min_t = float(sensor.min_threshold) if sensor.min_threshold is not None else None
        max_t = float(sensor.max_threshold) if sensor.max_threshold is not None else None

        if min_t is None and max_t is None:
            self.is_anomaly = False
            self.anomaly_score = None
            return

        deviation = 0.0
        is_out = False

        if min_t is not None and value < min_t:
            is_out = True
            range_size = abs(min_t) if min_t != 0 else 1
            deviation = abs(value - min_t) / max(abs(min_t), 1) * 100

        if max_t is not None and value > max_t:
            is_out = True
            range_size = abs(max_t) if max_t != 0 else 1
            deviation = abs(value - max_t) / max(abs(max_t), 1) * 100

        self.is_anomaly = is_out
        self.anomaly_score = round(deviation, 2) if is_out else None

    def __str__(self):
        return f'{self.sensor.name}: {self.value} {self.sensor.unit} @ {self.timestamp}'
