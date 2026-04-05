from django.urls import path
from .views import (
    SensorListCreateView,
    SensorDetailView,
    SensorReadingListView,
    SensorReadingCreateView,
    SensorAnomalyListView,
    SensorReadingBulkCreateView,
)

urlpatterns = [
    path('', SensorListCreateView.as_view(), name='sensor-list-create'),
    path('<int:pk>/', SensorDetailView.as_view(), name='sensor-detail'),
    path('<int:sensor_pk>/readings/', SensorReadingListView.as_view(), name='sensor-reading-list'),
    path('<int:sensor_pk>/readings/anomalies/', SensorAnomalyListView.as_view(), name='sensor-anomaly-list'),
    path('readings/', SensorReadingCreateView.as_view(), name='sensor-reading-create'),
    path('readings/bulk/', SensorReadingBulkCreateView.as_view(), name='sensor-reading-bulk-create'),
]
