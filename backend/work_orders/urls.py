from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WorkOrderViewSet, WorkOrderStatusViewSet, ErrorTypeViewSet

router = DefaultRouter()
router.register(r'status', WorkOrderStatusViewSet, basename='workorderstatus')
router.register(r'error-types', ErrorTypeViewSet, basename='errortype')
router.register(r'', WorkOrderViewSet, basename='workorder')

urlpatterns = [
    path('', include(router.urls)),
]
