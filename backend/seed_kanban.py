from work_orders.models import WorkOrderStatus, ErrorType
import sys

def seed():
    statuses = [
        {'name': 'A Fazer', 'order_index': 1, 'is_closed': False},
        {'name': 'Em Andamento', 'order_index': 2, 'is_closed': False},
        {'name': 'Concluída', 'order_index': 3, 'is_closed': True},
        {'name': 'Cancelada', 'order_index': 4, 'is_closed': True},
    ]

    for s in statuses:
        WorkOrderStatus.objects.get_or_create(name=s['name'], defaults=s)

    errors = [
        {'name': 'Erro de Sensor', 'description': 'Falhas na captação ou envio de telemetria.'},
        {'name': 'Falha na Máquina', 'description': 'Problema físico e mecânico do equipamento.'},
        {'name': 'Manutenção de Rotina', 'description': 'Inspeção e lubrificação periódica padrão.'},
        {'name': 'Calibração', 'description': 'Ajuste de medidas ou sensores desviados.'},
        {'name': 'Correção Geral', 'description': 'Outros problemas imprevistos.'},
    ]

    for e in errors:
        ErrorType.objects.get_or_create(name=e['name'], defaults=e)

    print('Seed finalizado.')

if __name__ == '__main__':
    seed()
