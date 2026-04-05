from django.core.management.base import BaseCommand
from suppliers.models import Supplier
from django.contrib.auth import get_user_model

User = get_user_model()

SUPPLIERS = [
    {
        'name': 'TechSensors Industria Ltda',
        'cnpj': '12.345.678/0001-90',
        'email': 'contato@techsensors.com.br',
        'phone': '(11) 3333-4444',
        'address': 'Av. Industrial, 1500',
        'city': 'Sao Paulo',
        'state': 'SP',
        'contact_name': 'Marcos Ferreira',
        'contact_email': 'marcos@techsensors.com.br',
        'description': 'Fornecedor de sensores industriais de alta precisao.',
        'is_active': True,
    },
    {
        'name': 'AutoMaq Pecas e Componentes',
        'cnpj': '98.765.432/0001-10',
        'email': 'vendas@automaq.com.br',
        'phone': '(21) 4444-5555',
        'address': 'Rua das Fabricas, 800',
        'city': 'Rio de Janeiro',
        'state': 'RJ',
        'contact_name': 'Patricia Oliveira',
        'contact_email': 'patricia@automaq.com.br',
        'description': 'Pecas e componentes para maquinas industriais diversas.',
        'is_active': True,
    },
    {
        'name': 'EletroIndustria Distribuidora',
        'cnpj': '11.222.333/0001-44',
        'email': 'eletro@eletroindustria.com.br',
        'phone': '(31) 5555-6666',
        'address': 'Rod. BR-040, KM 12',
        'city': 'Belo Horizonte',
        'state': 'MG',
        'contact_name': 'Lucas Almeida',
        'contact_email': 'lucas@eletroindustria.com.br',
        'description': 'Distribuidora de componentes eletronicos industriais.',
        'is_active': True,
    },
    {
        'name': 'Manutex Servicos Industriais',
        'cnpj': '44.555.666/0001-77',
        'email': 'manutex@manutex.com.br',
        'phone': '(41) 7777-8888',
        'address': 'Rua Manutencao, 300',
        'city': 'Curitiba',
        'state': 'PR',
        'contact_name': 'Fernanda Costa',
        'contact_email': 'fernanda@manutex.com.br',
        'description': 'Prestacao de servicos de manutencao preventiva e corretiva.',
        'is_active': True,
    },
    {
        'name': 'RoboTech Automacao Industrial',
        'cnpj': '55.666.777/0001-88',
        'email': 'robotech@robotech.ind.br',
        'phone': '(51) 6666-7777',
        'address': 'Av. Tecnologia, 2200',
        'city': 'Porto Alegre',
        'state': 'RS',
        'contact_name': 'Eduardo Ramos',
        'contact_email': 'eduardo@robotech.ind.br',
        'description': 'Automacao industrial e robotica para linhas de producao.',
        'is_active': False,
    },
]


class Command(BaseCommand):
    help = 'Cria fornecedores de exemplo para o PredictAI'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove fornecedores existentes antes de criar novos.',
        )

    def handle(self, *args, **options):
        if options['reset']:
            deleted, _ = Supplier.objects.all().delete()
            self.stdout.write(self.style.WARNING(f'Removidos {deleted} fornecedores existentes.'))

        admin_user = User.objects.filter(system_role='ADMIN').first()
        created_count = 0

        for data in SUPPLIERS:
            cnpj = data['cnpj']
            if Supplier.objects.filter(cnpj=cnpj).exists():
                self.stdout.write(self.style.WARNING(f'  Ja existe: {data["name"]}'))
                continue

            supplier = Supplier.objects.create(created_by=admin_user, **data)
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'  Criado: {supplier.name}'))

        self.stdout.write(self.style.SUCCESS(
            f'\nSeed concluido: {created_count} fornecedor(es) criado(s).'
        ))
