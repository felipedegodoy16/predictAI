from django.contrib import admin
from .models import Alert


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'machine', 'alert_type', 'risk_level', 'status', 'created_at']
    list_filter = ['risk_level', 'status', 'alert_type']
    search_fields = ['title', 'message', 'machine__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'resolved_at', 'resolved_by']
