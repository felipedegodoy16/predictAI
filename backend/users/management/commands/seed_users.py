from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

USERS = [
    {
        'name': 'Admin PredictAI',
        'email': 'admin@predictai.com',
        'cpf': '000.000.000-00',
        'username': 'admin',
        'system_role': 'ADMIN',
        'company_role': 'DIRECTOR',
        'department': 'TI',
        'phone': '(11) 99999-0000',
        'password': 'admin123456',
        'is_staff': True,
        'is_superuser': True,
    },
    {
        'name': 'Carlos Souza',
        'email': 'carlos.souza@predictai.com',
        'cpf': '111.222.333-44',
        'username': 'carlos.souza',
        'system_role': 'TECHNICIAN',
        'company_role': 'TECHNICIAN',
        'department': 'Manutencao',
        'phone': '(11) 98888-1111',
        'password': 'tecnico123456',
    },
    {
        'name': 'Ana Lima',
        'email': 'ana.lima@predictai.com',
        'cpf': '222.333.444-55',
        'username': 'ana.lima',
        'system_role': 'TECHNICIAN',
        'company_role': 'ANALYST',
        'department': 'Manutencao',
        'phone': '(11) 97777-2222',
        'password': 'tecnico123456',
    },
    {
        'name': 'Roberto Dias',
        'email': 'roberto.dias@predictai.com',
        'cpf': '333.444.555-66',
        'username': 'roberto.dias',
        'system_role': 'MANAGER',
        'company_role': 'MANAGER',
        'department': 'Operacoes',
        'phone': '(11) 96666-3333',
        'password': 'gestor123456',
    },
]


class Command(BaseCommand):
    help = 'Cria usuarios de exemplo para o PredictAI'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove usuarios existentes antes de criar novos (exceto superusers do sistema)',
        )

    def handle(self, *args, **options):
        if options['reset']:
            deleted, _ = User.objects.filter(email__endswith='@predictai.com').delete()
            self.stdout.write(self.style.WARNING(f'Removidos {deleted} usuarios existentes.'))

        created_count = 0
        for data in USERS:
            email = data['email']
            if User.objects.filter(email=email).exists():
                self.stdout.write(self.style.WARNING(f'  Ja existe: {email}'))
                continue

            password = data.pop('password')
            user = User(**data)
            user.set_password(password)
            user.save()
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'  Criado: {user.name} ({user.system_role})'))

        self.stdout.write(self.style.SUCCESS(
            f'\nSeed concluido: {created_count} usuario(s) criado(s).'
        ))
        self.stdout.write('Credenciais:')
        self.stdout.write('  admin@predictai.com        / admin123456   (ADMIN)')
        self.stdout.write('  carlos.souza@predictai.com / tecnico123456 (TECHNICIAN)')
        self.stdout.write('  ana.lima@predictai.com     / tecnico123456 (TECHNICIAN)')
        self.stdout.write('  roberto.dias@predictai.com / gestor123456  (MANAGER)')
