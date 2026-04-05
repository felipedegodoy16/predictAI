from django.contrib import admin
from .models import Sensor, SensorReading


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ['name', 'sensor_type', 'machine', 'unit', 'min_threshold', 'max_threshold', 'is_active']
    list_filter = ['sensor_type', 'is_active', 'machine']
    search_fields = ['name', 'machine__name']
    ordering = ['machine__name', 'name']


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ['sensor', 'value', 'timestamp', 'is_anomaly', 'anomaly_score']
    list_filter = ['is_anomaly', 'sensor__sensor_type']
    search_fields = ['sensor__name', 'sensor__machine__name']
    ordering = ['-timestamp']
    readonly_fields = ['is_anomaly', 'anomaly_score', 'created_at']
