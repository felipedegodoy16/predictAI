from django.db import models
from django.conf import settings
from machines.models import Machine

class WorkOrderStatus(models.Model):
    name = models.CharField(max_length=50)
    order_index = models.IntegerField(default=0)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ['order_index']

    def __str__(self):
        return self.name

class ErrorType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class WorkOrder(models.Model):
    class Priority(models.TextChoices):
        LOW = 'LOW', 'Baixa'
        MEDIUM = 'MEDIUM', 'Media'
        HIGH = 'HIGH', 'Alta'
        CRITICAL = 'CRITICAL', 'Critica'

    class OrderType(models.TextChoices):
        MANUAL = 'MANUAL', 'Manual'
        PREVENTIVE = 'PREVENTIVE', 'Preventiva'
        PREDICTIVE = 'PREDICTIVE', 'Preditiva'

    title = models.CharField(max_length=255)
    description = models.TextField()
    machine = models.ForeignKey(
        Machine, on_delete=models.CASCADE, null=True, blank=True, related_name='work_orders'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_work_orders'
    )
    status = models.ForeignKey(
        WorkOrderStatus, on_delete=models.PROTECT, related_name='work_orders', null=True
    )
    error_type = models.ForeignKey(
        ErrorType, on_delete=models.SET_NULL, null=True, blank=True, related_name='work_orders'
    )
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    order_type = models.CharField(max_length=20, choices=OrderType.choices, default=OrderType.MANUAL)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_work_orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title}"
