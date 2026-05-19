from django.db import models
from django.conf import settings
from machines.models import Machine
from alerts.models import Alert

class WorkOrder(models.Model):
    class OrderType(models.TextChoices):
        EMERGENCIAL = 'emergencial', 'Emergencial'
        PREDITIVA = 'preditiva', 'Preditiva'
        PREVENTIVA = 'preventiva', 'Preventiva'
        CORRETIVA = 'corretiva', 'Corretiva'

    class Status(models.TextChoices):
        ABERTA = 'aberta', 'Aberta'
        EM_ANDAMENTO = 'em_andamento', 'Em Andamento'
        CONCLUIDA = 'concluida', 'Concluida'
        CANCELADA = 'cancelada', 'Cancelada'

    class Priority(models.TextChoices):
        BAIXA = 'baixa', 'Baixa'
        MEDIA = 'media', 'Media'
        ALTA = 'alta', 'Alta'
        CRITICA = 'critica', 'Critica'

    alert = models.ForeignKey(Alert, on_delete=models.SET_NULL, null=True, blank=True, related_name='work_orders')
    previous_maintenance = models.ForeignKey('Maintenance', on_delete=models.SET_NULL, null=True, blank=True, related_name='next_orders')
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='work_orders')
    opened_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='opened_orders')
    
    order_type = models.CharField(max_length=20, choices=OrderType.choices)
    production_line = models.CharField(max_length=100)
    temperature = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ABERTA)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIA)
    observation = models.TextField(null=True, blank=True)
    
    opening_date = models.DateTimeField(auto_now_add=True)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    completion_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-opening_date']

    def __str__(self):
        return f'OS-{self.id} - {self.machine.serial_number}'

class Maintenance(models.Model):
    work_order = models.OneToOneField(WorkOrder, on_delete=models.CASCADE, related_name='maintenance')
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='maintenances')
    description = models.TextField(null=True, blank=True)
    solution = models.TextField(null=True, blank=True)
    next_maintenance_deadline = models.IntegerField(null=True, blank=True, help_text="Prazo para a proxima manutencao (em dias)")
    performed_date = models.DateTimeField()

    class Meta:
        ordering = ['-performed_date']

    def __str__(self):
        return f'Manutencao OS-{self.work_order.id}'
