from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import WorkOrder
from notifications.models import Notification

# Removido signals quebrados que procuravam assigned_to e title
