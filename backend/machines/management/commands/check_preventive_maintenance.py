from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import datetime
from machines.models import Machine
from work_orders.models import WorkOrder, WorkOrderStatus

class Command(BaseCommand):
    help = 'Gera OS preventiva automaticamente para máquinas que atingiram o intervalo.'

    def handle(self, *args, **options):
        machines = Machine.objects.filter(preventive_maintenance_interval__isnull=False, preventive_maintenance_interval__gt=0)
        
        todo_status = WorkOrderStatus.objects.order_by('order_index').first()
        if not todo_status:
            self.stdout.write(self.style.ERROR('Nenhum WorkOrderStatus encontrado. Não é possível criar OS.'))
            return
            
        created_count = 0
        now = timezone.now()
        
        for machine in machines:
            last_preventiva = WorkOrder.objects.filter(
                machine=machine,
                order_type=WorkOrder.OrderType.PREVENTIVA
            ).order_by('-opening_date').first()
            
            if last_preventiva:
                base_date = last_preventiva.opening_date
            elif machine.installation_date:
                base_date = timezone.make_aware(datetime.datetime.combine(machine.installation_date, datetime.time.min))
            else:
                continue 
                
            interval = timedelta(days=machine.preventive_maintenance_interval)
            
            if (now - base_date) >= interval:
                open_statuses = WorkOrderStatus.objects.filter(is_closed=False)
                has_open_preventiva = WorkOrder.objects.filter(
                    machine=machine,
                    order_type=WorkOrder.OrderType.PREVENTIVA,
                    status__in=open_statuses
                ).exists()
                
                if not has_open_preventiva:
                    WorkOrder.objects.create(
                        machine=machine,
                        order_type=WorkOrder.OrderType.PREVENTIVA,
                        production_line=machine.production_line or 'Não informada',
                        priority=WorkOrder.Priority.MEDIA,
                        status=todo_status,
                        observation='OS gerada automaticamente por tempo de uso (manutenção preventiva).',
                    )
                    created_count += 1
                    self.stdout.write(self.style.SUCCESS(f'OS Preventiva criada para máquina {machine.serial_number}'))
                    
        self.stdout.write(self.style.SUCCESS(f'Processo concluído. {created_count} OS preventivas criadas.'))
