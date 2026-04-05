from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['name', 'email', 'cpf', 'system_role', 'company_role', 'is_active', 'created_at']
    list_filter = ['system_role', 'company_role', 'is_active']
    search_fields = ['name', 'email', 'cpf']
    ordering = ['name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Dados Pessoais', {'fields': ('name', 'cpf', 'phone', 'department', 'username')}),
        ('Papeis', {'fields': ('system_role', 'company_role')}),
        ('Permissoes', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    readonly_fields = ['created_at', 'updated_at', 'last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'name', 'cpf', 'system_role', 'company_role', 'password1', 'password2'),
        }),
    )
