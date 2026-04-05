from django.core.management.base import BaseCommand
from machines.models import Machine
from sensors.models import Sensor
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

MACHINES = [
    {
        'name': 'Compressor Industrial A1',
        'serial_number': 'COMP-A1-2021-001',
        'model': 'CP-5000',
        'manufacturer': 'Atlas Copco',
        'location': 'Galpao A - Linha 1',
        'description': 'Compressor de ar industrial principal da linha de producao.',
        'status': 'ACTIVE',
        'installation_date': '2021-03-15',
        'sensors': [
            {'name': 'Sensor de Temperatura Motor', 'sensor_type': 'TEMPERATURE', 'unit': 'C',
             'min_threshold': 20, 'max_threshold': 85},
            {'name': 'Sensor de Vibracao', 'sensor_type': 'VIBRATION', 'unit': 'mm/s',
             'min_threshold': 0, 'max_threshold': 7.5},
            {'name': 'Sensor de Pressao Saida', 'sensor_type': 'PRESSURE', 'unit': 'bar',
             'min_threshold': 6.0, 'max_threshold': 10.0},
            {'name': 'Sensor de Corrente Motor', 'sensor_type': 'CURRENT', 'unit': 'A',
             'min_threshold': 5, 'max_threshold': 40},
        ],
    },
    {
        'name': 'Torno CNC T200',
        'serial_number': 'TORNO-T200-2020-003',
        'model': 'T-200 CNC',
        'manufacturer': 'Romi',
        'location': 'Galpao B - Linha 2',
        'description': 'Torno CNC para usinagem de precisao.',
        'status': 'ACTIVE',
        'installation_date': '2020-07-22',
        'sensors': [
            {'name': 'Temperatura do Spindle', 'sensor_type': 'TEMPERATURE', 'unit': 'C',
             'min_threshold': 15, 'max_threshold': 70},
            {'name': 'Vibracao do Eixo', 'sensor_type': 'VIBRATION', 'unit': 'mm/s',
             'min_threshold': 0, 'max_threshold': 5.0},
            {'name': 'RPM do Spindle', 'sensor_type': 'RPM', 'unit': 'RPM',
             'min_threshold': 100, 'max_threshold': 3500},
        ],
    },
    {
        'name': 'Esteira Transportadora L1',
        'serial_number': 'ESTEIRA-L1-2022-007',
        'model': 'ET-100',
        'manufacturer': 'Tramontina Industrial',
        'location': 'Galpao A - Corredor Central',
        'description': 'Esteira de transporte de peas entre linhas de producao.',
        'status': 'ACTIVE',
        'installation_date': '2022-01-10',
        'sensors': [
            {'name': 'Sensor de Velocidade', 'sensor_type': 'RPM', 'unit': 'm/min',
             'min_threshold': 0.5, 'max_threshold': 15},
            {'name': 'Temperatura Motor Esteira', 'sensor_type': 'TEMPERATURE', 'unit': 'C',
             'min_threshold': 15, 'max_threshold': 65},
            {'name': 'Corrente Motor Esteira', 'sensor_type': 'CURRENT', 'unit': 'A',
             'min_threshold': 2, 'max_threshold': 20},
        ],
    },
    {
        'name': 'Bomba Hidraulica BH-3',
        'serial_number': 'BOMBA-BH3-2019-012',
        'model': 'BH-3000',
        'manufacturer': 'Rexnord',
        'location': 'Sala de Maquinas - Subsolo',
        'description': 'Bomba hidraulica do sistema de resfriamento.',
        'status': 'MAINTENANCE',
        'installation_date': '2019-11-05',
        'sensors': [
            {'name': 'Pressao de Entrada', 'sensor_type': 'PRESSURE', 'unit': 'bar',
             'min_threshold': 1.5, 'max_threshold': 8.0},
            {'name': 'Pressao de Saida', 'sensor_type': 'PRESSURE', 'unit': 'bar',
             'min_threshold': 3.0, 'max_threshold': 15.0},
            {'name': 'Temperatura Fluido', 'sensor_type': 'TEMPERATURE', 'unit': 'C',
             'min_threshold': 10, 'max_threshold': 60},
            {'name': 'Vibracao Bomba', 'sensor_type': 'VIBRATION', 'unit': 'mm/s',
             'min_threshold': 0, 'max_threshold': 6.0},
        ],
    },
    {
        'name': 'Gerador Eletrico GE-1',
        'serial_number': 'GER-GE1-2018-005',
        'model': 'GE-250KVA',
        'manufacturer': 'Cummins',
        'location': 'Area Externa - Subestacao',
        'description': 'Gerador eletrico de emergencia 250 KVA.',
        'status': 'INACTIVE',
        'installation_date': '2018-06-20',
        'sensors': [
            {'name': 'Tensao de Saida', 'sensor_type': 'VOLTAGE', 'unit': 'V',
             'min_threshold': 198, 'max_threshold': 242},
            {'name': 'Corrente de Saida', 'sensor_type': 'CURRENT', 'unit': 'A',
             'min_threshold': 0, 'max_threshold': 360},
            {'name': 'Temperatura Motor Gerador', 'sensor_type': 'TEMPERATURE', 'unit': 'C',
             'min_threshold': 20, 'max_threshold': 95},
            {'name': 'RPM Motor Gerador', 'sensor_type': 'RPM', 'unit': 'RPM',
             'min_threshold': 1700, 'max_threshold': 1850},
        ],
    },
    {
        'name': 'Injetora de Plastico IP-2',
        'serial_number': 'INJET-IP2-2023-001',
        'model': 'IP-850T',
        'manufacturer': 'Romi',
        'location': 'Galpao C - Linha 3',
        'description': 'Injetora de plastico para producao de pecas automotivas.',
        'status': 'ACTIVE',
        'installation_date': '2023-03-01',
        'sensors': [
            {'name': 'Temperatura de Injecao', 'sensor_type': 'TEMPERATURE', 'unit': 'C',
             'min_threshold': 180, 'max_threshold': 280},
            {'name': 'Pressao de Injecao', 'sensor_type': 'PRESSURE', 'unit': 'bar',
             'min_threshold': 50, 'max_threshold': 200},
            {'name': 'Temperatura do Molde', 'sensor_type': 'TEMPERATURE', 'unit': 'C',
             'min_threshold': 20, 'max_threshold': 80},
            {'name': 'Umidade Relativa Ambiente', 'sensor_type': 'HUMIDITY', 'unit': '%',
             'min_threshold': 20, 'max_threshold': 70},
        ],
    },
]


class Command(BaseCommand):
    help = 'Cria maquinas e sensores de exemplo para o PredictAI'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove maquinas e sensores existentes antes de criar novos.',
        )

    def handle(self, *args, **options):
        if options['reset']:
            deleted, _ = Machine.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Removidas {deleted} maquinas existentes (e seus sensores/leituras).'))

        admin_user = User.objects.filter(system_role='ADMIN').first()
        machines_created = 0
        sensors_created = 0

        for data in MACHINES:
            sensors_data = data.pop('sensors')
            serial = data['serial_number']

            if Machine.objects.filter(serial_number=serial).exists():
                self.stdout.write(self.style.WARNING(f'  Ja existe: {data["name"]}'))
                continue

            machine = Machine.objects.create(created_by=admin_user, **data)
            machines_created += 1
            self.stdout.write(self.style.SUCCESS(f'  Maquina criada: {machine.name} [{machine.status}]'))

            for sensor_data in sensors_data:
                Sensor.objects.create(machine=machine, **sensor_data)
                sensors_created += 1

            self.stdout.write(f'    -> {len(sensors_data)} sensor(es) criado(s)')

        self.stdout.write(self.style.SUCCESS(
            f'\nSeed concluido: {machines_created} maquina(s) e {sensors_created} sensor(es) criado(s).'
        ))
