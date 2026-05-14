from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import WorkOrder
from notifications.models import Notification

@receiver(pre_save, sender=WorkOrder)
def work_order_pre_save(sender, instance, **kwargs):
    if instance.pk:
        # Pega a versão anterior do banco de dados
        try:
            old_instance = WorkOrder.objects.get(pk=instance.pk)
            instance._old_assigned_to = old_instance.assigned_to
        except WorkOrder.DoesNotExist:
            instance._old_assigned_to = None
    else:
        instance._old_assigned_to = None

@receiver(post_save, sender=WorkOrder)
def create_notification_for_work_order(sender, instance, created, **kwargs):
    if created:
        if instance.assigned_to:
            Notification.objects.create(
                user=instance.assigned_to,
                title="Nova Ordem de Serviço",
                message=f"Foi atribuída a você uma nova Ordem de Serviço: {instance.title}. Prioridade: {instance.get_priority_display()}.",
                notification_type=Notification.NotificationType.INFO
            )
    else:
        # Check if assigned_to changed
        old_assigned = getattr(instance, '_old_assigned_to', None)
        if instance.assigned_to and instance.assigned_to != old_assigned:
            Notification.objects.create(
                user=instance.assigned_to,
                title="Ordem de Serviço Atribuída",
                message=f"A Ordem de Serviço: {instance.title} foi atribuída a você. Prioridade: {instance.get_priority_display()}.",
                notification_type=Notification.NotificationType.INFO
            )
