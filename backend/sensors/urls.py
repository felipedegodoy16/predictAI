from django.urls import path
from .views import (
    SensorListCreateView,
    SensorDetailView,
    SensorReadingListView,
    SensorReadingCreateView,
    SensorReadingBulkCreateView,
)

urlpatterns = [
    path('', SensorListCreateView.as_view(), name='sensor-list-create'),
    path('<int:pk>/', SensorDetailView.as_view(), name='sensor-detail'),
    path('<int:sensor_pk>/readings/', SensorReadingListView.as_view(), name='sensor-reading-list'),
    path('readings/', SensorReadingCreateView.as_view(), name='sensor-reading-create'),
    path('readings/bulk/', SensorReadingBulkCreateView.as_view(), name='sensor-reading-bulk-create'),
]
