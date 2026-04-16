from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from machines.models import Machine
from work_orders.models import WorkOrder

class Command(BaseCommand):
    help = 'Gera Ordens de Servico Preditivas para maquinas que atingiram o prazo'

    def handle(self, *args, **options):
        today = timezone.now().date()
        machines = Machine.objects.filter(maintenance_interval_days__isnull=False)
        created_count = 0

        for machine in machines:
            last_date = machine.last_maintenance_date or machine.installation_date
            if not last_date:
                continue
                
            next_maintenance = last_date + timedelta(days=machine.maintenance_interval_days)
            
            if today >= next_maintenance:
                # Verifica se ja existe uma OS preventiva aberta para essa maquina
                has_open_os = WorkOrder.objects.filter(
                    machine=machine,
                    order_type=WorkOrder.OrderType.PREVENTIVE,
                    status__is_closed=False
                ).exists()

                if not has_open_os:
                    WorkOrder.objects.create(
                        title=f'Manutencao Preventiva: {machine.name}',
                        description=f'O prazo de {machine.maintenance_interval_days} dias desde a ultima manutencao foi atingido.',
                        machine=machine,
                        order_type=WorkOrder.OrderType.PREVENTIVE,
                        priority=WorkOrder.Priority.MEDIUM
                    )
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'OS Preventiva criada para {machine.name}'))

        self.stdout.write(self.style.SUCCESS(f'Finalizado. {created_count} OS(s) criadas.'))
