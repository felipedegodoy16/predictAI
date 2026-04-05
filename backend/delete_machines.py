import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
django.setup()

from machines.models import Machine
Machine.objects.all().delete()
print("Todas as maquinas removidas com sucesso.")
