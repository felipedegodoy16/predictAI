from django.db import models
from django.urls import path
from .views import (
    MachineListCreateView,
    MachineDetailView,
    MachineStatusUpdateView,
)

urlpatterns = [
    path('', MachineListCreateView.as_view(), name='machine-list-create'),
    path('<int:pk>/', MachineDetailView.as_view(), name='machine-detail'),
    path('<int:pk>/status/', MachineStatusUpdateView.as_view(), name='machine-status-update'),
]
