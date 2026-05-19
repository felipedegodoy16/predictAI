from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    table_name = models.CharField(max_length=50)
    record_id = models.IntegerField()
    field_name = models.CharField(max_length=100)
    old_value = models.CharField(max_length=255, null=True, blank=True)
    new_value = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        username = self.user.name if self.user else 'Sistema'
        return f"{username} - {self.table_name}.{self.field_name} ({self.timestamp})"
