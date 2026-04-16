from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WorkOrder
from notifications.models import Notification

@receiver(post_save, sender=WorkOrder)
def create_notification_for_work_order(sender, instance, created, **kwargs):
    if created and instance.assigned_to:
        Notification.objects.create(
            user=instance.assigned_to,
            title="Nova Ordem de Serviço",
            message=f"Foi atribuída a você uma nova Ordem de Serviço: {instance.title}. Prioridade: {instance.get_priority_display()}.",
            notification_type=Notification.NotificationType.INFO
        )
