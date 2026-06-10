import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "predictAI.settings")
django.setup()

from django.test import Client
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

client = APIClient()
client.force_authenticate(user=user)

from work_orders.models import WorkOrder, WorkOrderStatus

wo = WorkOrder.objects.first()
if not wo:
    print("No work orders found")
else:
    status = WorkOrderStatus.objects.last()
    print(f"Moving OS {wo.id} to status {status.id}")
    response = client.patch(f"/api/work-orders/{wo.id}/move_status/", {"status": status.id}, format="json")
    print(f"Status Code: {response.status_code}")
    print(f"Content: {response.content.decode('utf-8')}")
