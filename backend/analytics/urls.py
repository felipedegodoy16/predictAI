from django.urls import path
from .views import (
    DashboardView,
    MachinePatternsView,
    FailurePredictionView,
    MaintenanceSuggestionsView,
    ChartDataView,
    OSTelemetryView,
    SensorProblemsView,
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='analytics-dashboard'),
    path('charts/', ChartDataView.as_view(), name='analytics-charts'),
    path('machines/<int:machine_id>/patterns/', MachinePatternsView.as_view(), name='analytics-patterns'),
    path('machines/<int:machine_id>/failure-prediction/', FailurePredictionView.as_view(), name='analytics-failure-prediction'),
    path('maintenance-suggestions/', MaintenanceSuggestionsView.as_view(), name='analytics-maintenance-suggestions'),
    path('os-telemetry/<int:os_id>/', OSTelemetryView.as_view(), name='analytics-os-telemetry'),
    path('sensor-problems/', SensorProblemsView.as_view(), name='analytics-sensor-problems'),
]
