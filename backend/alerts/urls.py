from django.urls import path
from .views import (
    AlertListCreateView,
    AlertDetailView,
    AlertAcknowledgeView,
    AlertResolveView,
    OpenAlertsView,
    HighRiskAlertsView,
)

urlpatterns = [
    path('', AlertListCreateView.as_view(), name='alert-list-create'),
    path('<int:pk>/', AlertDetailView.as_view(), name='alert-detail'),
    path('<int:pk>/acknowledge/', AlertAcknowledgeView.as_view(), name='alert-acknowledge'),
    path('<int:pk>/resolve/', AlertResolveView.as_view(), name='alert-resolve'),
    path('open/', OpenAlertsView.as_view(), name='alert-open'),
    path('high-risk/', HighRiskAlertsView.as_view(), name='alert-high-risk'),
]
