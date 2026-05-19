from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkOrderViewSet, MaintenanceViewSet

router = DefaultRouter()
router.register(r'maintenances', MaintenanceViewSet, basename='maintenance')
router.register(r'', WorkOrderViewSet, basename='workorder')

urlpatterns = [
    path('', include(router.urls)),
]
