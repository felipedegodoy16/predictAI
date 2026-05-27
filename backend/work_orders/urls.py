from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkOrderViewSet, MaintenanceViewSet, WorkOrderStatusViewSet

router = DefaultRouter()
router.register(r'maintenances', MaintenanceViewSet, basename='maintenance')
router.register(r'status', WorkOrderStatusViewSet, basename='workorderstatus')
router.register(r'', WorkOrderViewSet, basename='workorder')

urlpatterns = [
    path('', include(router.urls)),
]
