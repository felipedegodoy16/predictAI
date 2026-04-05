from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('auth_jwt.urls')),
    path('api/users/', include('users.urls')),
    path('api/machines/', include('machines.urls')),
    path('api/sensors/', include('sensors.urls')),
    path('api/alerts/', include('alerts.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/suppliers/', include('suppliers.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/audit/', include('audit.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
