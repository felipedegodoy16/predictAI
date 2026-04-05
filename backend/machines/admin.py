from django.contrib import admin
from .models import Machine


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ['name', 'serial_number', 'supplier', 'location', 'status', 'created_at']
    list_filter = ['status', 'supplier']
    search_fields = ['name', 'serial_number', 'model', 'supplier__name']
    ordering = ['name']
    readonly_fields = ['api_key', 'created_by', 'created_at', 'updated_at']
