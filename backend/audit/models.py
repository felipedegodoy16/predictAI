from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = 'CREATE', 'Criado'
        UPDATE = 'UPDATE', 'Atualizado'
        DELETE = 'DELETE', 'Deletado'
        ACTION = 'ACTION', 'Acao Especial'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=20, choices=Action.choices)
    entity_type = models.CharField(max_length=100) # Ex: Machine, Supplier, User
    entity_id = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        username = self.user.name if self.user else 'Sistema'
        return f"{username} - {self.action} - {self.entity_type} ({self.timestamp})"
