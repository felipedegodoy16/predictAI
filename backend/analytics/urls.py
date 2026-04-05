from django.urls import path
from .views import (
    DashboardView,
    MachinePatternsView,
    FailurePredictionView,
    MaintenanceSuggestionsView,
)

urlpatterns = [
    path('dashboard/', DashboardView.as_view(), name='analytics-dashboard'),
    path('machines/<int:machine_id>/patterns/', MachinePatternsView.as_view(), name='analytics-patterns'),
    path('machines/<int:machine_id>/failure-prediction/', FailurePredictionView.as_view(), name='analytics-failure-prediction'),
    path('maintenance-suggestions/', MaintenanceSuggestionsView.as_view(), name='analytics-maintenance-suggestions'),
]
