from django.db import models
from django.conf import settings


class Alert(models.Model):
    class AlertType(models.TextChoices):
        ANOMALY = 'ANOMALY', 'Anomalia'
        THRESHOLD = 'THRESHOLD', 'Limite Ultrapassado'
        PREDICTIVE = 'PREDICTIVE', 'Preditivo'
        MANUAL = 'MANUAL', 'Manual'

    class RiskLevel(models.TextChoices):
        LOW = 'LOW', 'Baixo'
        MEDIUM = 'MEDIUM', 'Medio'
        HIGH = 'HIGH', 'Alto'

    class AlertStatus(models.TextChoices):
        OPEN = 'OPEN', 'Aberto'
        ACKNOWLEDGED = 'ACKNOWLEDGED', 'Reconhecido'
        RESOLVED = 'RESOLVED', 'Resolvido'

    machine = models.ForeignKey(
        'machines.Machine', on_delete=models.CASCADE, related_name='alerts'
    )
    sensor = models.ForeignKey(
        'sensors.Sensor', on_delete=models.SET_NULL, null=True, blank=True, related_name='alerts'
    )
    reading = models.ForeignKey(
        'sensors.SensorReading', on_delete=models.SET_NULL, null=True, blank=True, related_name='alerts'
    )
    alert_type = models.CharField(max_length=20, choices=AlertType.choices, default=AlertType.THRESHOLD)
    risk_level = models.CharField(max_length=10, choices=RiskLevel.choices, default=RiskLevel.LOW)
    status = models.CharField(max_length=20, choices=AlertStatus.choices, default=AlertStatus.OPEN)
    title = models.CharField(max_length=255)
    message = models.TextField()
    recommendation = models.TextField(blank=True, default='')
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts',
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['risk_level', '-created_at']),
            models.Index(fields=['machine', '-created_at']),
        ]

    def __str__(self):
        return f'[{self.risk_level}] {self.title} - {self.machine.name}'
