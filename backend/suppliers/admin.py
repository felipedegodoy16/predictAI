from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'cnpj', 'email', 'phone', 'city', 'state', 'is_active']
    list_filter = ['is_active', 'state']
    search_fields = ['name', 'cnpj', 'contact_name']
    ordering = ['name']
    readonly_fields = ['created_by', 'created_at', 'updated_at']
