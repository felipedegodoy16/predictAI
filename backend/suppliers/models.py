from django.db import models
from django.conf import settings


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True)
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')
    address = models.CharField(max_length=255, blank=True, default='')
    city = models.CharField(max_length=100, blank=True, default='')
    state = models.CharField(max_length=2, blank=True, default='')
    contact_name = models.CharField(max_length=255, blank=True, default='')
    contact_email = models.EmailField(blank=True, default='')
    description = models.TextField(blank=True, default='')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='suppliers_created',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.cnpj})'
