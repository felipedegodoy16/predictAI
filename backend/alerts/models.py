from django.db import models
from machines.models import Machine
from sensors.models import SensorReading

class Alert(models.Model):
    class AlertType(models.TextChoices):
        TEMP_ALTA = 'temp_alta', 'Temperatura Alta'
        VIBRACAO = 'vibracao', 'Vibracao'
        PRESSAO = 'pressao', 'Pressao'
        OUTRO = 'outro', 'Outro'

    class Criticality(models.TextChoices):
        BAIXA = 'baixa', 'Baixa'
        MEDIA = 'media', 'Media'
        ALTA = 'alta', 'Alta'

    reading = models.ForeignKey(SensorReading, on_delete=models.CASCADE, related_name='alerts')
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=20, choices=AlertType.choices, default=AlertType.TEMP_ALTA)
    detected_value = models.DecimalField(max_digits=8, decimal_places=2)
    limit_value = models.DecimalField(max_digits=8, decimal_places=2)
    criticality = models.CharField(max_length=10, choices=Criticality.choices, default=Criticality.MEDIA)
    viewed = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'[{self.get_criticality_display()}] {self.get_alert_type_display()} - {self.machine.serial_number}'
