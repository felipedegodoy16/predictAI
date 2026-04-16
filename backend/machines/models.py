import uuid
from django.db import models
from django.conf import settings


class Machine(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Ativa'
        MAINTENANCE = 'MAINTENANCE', 'Em Manutencao'
        INACTIVE = 'INACTIVE', 'Inativa'

    name = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=100, unique=True)
    model = models.CharField(max_length=100, blank=True, default='')
    location = models.CharField(max_length=255, blank=True, default='')
    description = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    installation_date = models.DateField(null=True, blank=True)
    maintenance_interval_days = models.PositiveIntegerField(null=True, blank=True, help_text="Intervalo em dias para manutencao preventiva")
    last_maintenance_date = models.DateField(null=True, blank=True)
    api_key = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='machines_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.serial_number})'
