from django.db import models

class Machine(models.Model):
    production_line = models.CharField(max_length=100, null=True, blank=True)
    manufacturer = models.CharField(max_length=100, null=True, blank=True)
    model = models.CharField(max_length=100, null=True, blank=True)
    serial_number = models.CharField(max_length=100, unique=True)
    installation_date = models.DateField(null=True, blank=True)
    telemetry_interval = models.IntegerField(default=0, help_text="Intervalo em minutos para armazenar leituras (0 = contínuo)")
    preventive_maintenance_interval = models.IntegerField(null=True, blank=True, help_text="Intervalo em dias para gerar OS preventiva automática")

    class Meta:
        ordering = ['production_line', 'manufacturer']

    def __str__(self):
        return f'{self.manufacturer} {self.model} ({self.serial_number})'

class MachineStatus(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ativa', 'Ativa'
        MAINTENANCE = 'manutencao', 'Manutencao'
        INACTIVE = 'inativa', 'Inativa'

    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='statuses')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    reason = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.machine.serial_number} - {self.get_status_display()}'
