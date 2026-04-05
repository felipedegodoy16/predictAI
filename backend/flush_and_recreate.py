import os
import django
from django.core.management import call_command

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

# Clean all tables
call_command('flush', '--no-input')

from users.models import User
# Recreate admin
User.objects.create_superuser(
    username='admin',
    email='admin@predictai.com',
    cpf='000.000.000-00',
    name='Admin System',
    password='admin',
    system_role='ADMIN',
    company_role='MANAGER'
)
print("Banco de Dados Flushado. Usuario admin@predictai.com criado com senha 'admin'")
