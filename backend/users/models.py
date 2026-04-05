from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class SystemRole(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        TECHNICIAN = 'TECHNICIAN', 'Tecnico'
        MANAGER = 'MANAGER', 'Gestor'

    class CompanyRole(models.TextChoices):
        MANAGER = 'MANAGER', 'Gerente'
        ANALYST = 'ANALYST', 'Analista'
        INTERN = 'INTERN', 'Estagiario'
        DIRECTOR = 'DIRECTOR', 'Diretor'
        TECHNICIAN = 'TECHNICIAN', 'Tecnico'
        OPERATOR = 'OPERATOR', 'Operador'

    username = models.CharField(max_length=150, unique=True, blank=True)
    name = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, default='')
    department = models.CharField(max_length=100, blank=True, default='')

    system_role = models.CharField(
        max_length=20,
        choices=SystemRole.choices,
        default=SystemRole.TECHNICIAN,
    )
    company_role = models.CharField(
        max_length=20,
        choices=CompanyRole.choices,
        default=CompanyRole.OPERATOR,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name', 'cpf']

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.system_role})'


class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_codes')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.code}"