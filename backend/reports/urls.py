from django.urls import path
from .views import FailureReportView, PerformanceReportView, AlertReportView

urlpatterns = [
    path('failures/', FailureReportView.as_view(), name='report-failures'),
    path('performance/', PerformanceReportView.as_view(), name='report-performance'),
    path('alerts/', AlertReportView.as_view(), name='report-alerts'),
]
