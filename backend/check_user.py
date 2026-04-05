import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from users.models import User

# List users
users = User.objects.all()
print(f"Total de usuarios: {users.count()}")

if users.exists():
    for u in users:
        print(f"- {u.email} (Username: {u.username})")
        u.set_password('admin')
        u.save()
        print("Senha resetada para 'admin'.")
else:
    print("Nenhum usuario encontrado! Criando um...")
    User.objects.create_superuser(
        username='admin',
        email='admin@predictai.com',
        cpf='000.000.000-00',
        name='Admin System',
        password='admin',
        system_role='ADMIN',
        company_role='MANAGER'
    )
    print("Admin criado.")
