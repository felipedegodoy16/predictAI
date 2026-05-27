"""
Seed das colunas Kanban de Ordens de Serviço.
Execute:  python seed_kanban.py
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from work_orders.models import WorkOrderStatus

STATUSES = [
    {"name": "To Do",       "order_index": 0, "is_closed": False},
    {"name": "In Progress", "order_index": 1, "is_closed": False},
    {"name": "Waiting",     "order_index": 2, "is_closed": False},
    {"name": "Done",        "order_index": 3, "is_closed": True},
]

created = 0
for s in STATUSES:
    obj, was_created = WorkOrderStatus.objects.get_or_create(
        name=s["name"],
        defaults={"order_index": s["order_index"], "is_closed": s["is_closed"]}
    )
    if was_created:
        print(f"  ✔ Criado: {obj.name}")
        created += 1
    else:
        print(f"  — Já existe: {obj.name}")

print(f"\nSeed concluído. {created} status(es) criado(s).")
