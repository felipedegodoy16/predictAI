import django, sys; django.setup(); from rest_framework.test import APIRequestFactory, force_authenticate; from users.models import User; from work_orders.models import WorkOrder; from work_orders.views import WorkOrderViewSet; factory = APIRequestFactory(); user = User.objects.first(); wo = WorkOrder.objects.first(); request = factory.patch(f'/api/work-orders/{wo.id}/move_status/', {'status': 2}, format='json'); force_authenticate(request, user=user); view = WorkOrderViewSet.as_view({'patch': 'move_status'});

try:
    res = view(request, pk=wo.id); print(res.data)
except Exception as e:
    import traceback; traceback.print_exc()
