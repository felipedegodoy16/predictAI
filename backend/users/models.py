from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Profile(models.TextChoices):
        ADMINISTRADOR = 'administrador', 'Administrador'
        GERENTE = 'gerente', 'Gerente'
        TECNICO = 'tecnico', 'Técnico'
        OPERADOR = 'operador', 'Operador'
        VISUALIZADOR = 'visualizador', 'Visualizador'

    # Removing unused AbstractUser fields where not needed, but we keep username since it's required by Django by default
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True, max_length=150)
    profile = models.CharField(
        max_length=20,
        choices=Profile.choices,
        default=Profile.VISUALIZADOR,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.get_profile_display()})'

class PasswordResetCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_codes')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.code}"