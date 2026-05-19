from django.urls import path
from .views import (
    AlertListCreateView,
    AlertDetailView,
    AlertMarkViewedView,
    UnviewedAlertsView,
    HighRiskAlertsView,
)

urlpatterns = [
    path('', AlertListCreateView.as_view(), name='alert-list-create'),
    path('unviewed/', UnviewedAlertsView.as_view(), name='alert-unviewed'),
    path('high-risk/', HighRiskAlertsView.as_view(), name='alert-high-risk'),
    path('<int:pk>/', AlertDetailView.as_view(), name='alert-detail'),
    path('<int:pk>/viewed/', AlertMarkViewedView.as_view(), name='alert-viewed'),
]
