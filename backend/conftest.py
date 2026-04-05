import pytest
from django.contrib.auth import get_user_model
from machines.models import Machine
from sensors.models import Sensor

User = get_user_model()


@pytest.fixture
def admin_user(db):
    return User.objects.create_user(
        email='admin@test.com',
        username='admin_test',
        name='Admin Teste',
        cpf='000.000.000-99',
        system_role='ADMIN',
        company_role='DIRECTOR',
        password='testpass123',
        is_staff=True,
    )


@pytest.fixture
def technician_user(db):
    return User.objects.create_user(
        email='tech@test.com',
        username='tech_test',
        name='Tecnico Teste',
        cpf='111.111.111-99',
        system_role='TECHNICIAN',
        company_role='TECHNICIAN',
        password='testpass123',
    )


@pytest.fixture
def manager_user(db):
    return User.objects.create_user(
        email='manager@test.com',
        username='manager_test',
        name='Gestor Teste',
        cpf='222.222.222-99',
        system_role='MANAGER',
        company_role='MANAGER',
        password='testpass123',
    )


@pytest.fixture
def machine(db, admin_user):
    return Machine.objects.create(
        name='Compressor Teste',
        serial_number='TEST-001',
        model='CP-TEST',
        manufacturer='Fabricante Teste',
        location='Galpao Teste',
        status='ACTIVE',
        created_by=admin_user,
    )


@pytest.fixture
def sensor(db, machine):
    return Sensor.objects.create(
        machine=machine,
        name='Sensor Temperatura Teste',
        sensor_type='TEMPERATURE',
        unit='C',
        min_threshold=10,
        max_threshold=80,
        is_active=True,
    )


@pytest.fixture
def sensor_no_threshold(db, machine):
    return Sensor.objects.create(
        machine=machine,
        name='Sensor Sem Limites',
        sensor_type='OTHER',
        unit='unit',
        is_active=True,
    )


@pytest.fixture
def admin_client(client, admin_user):
    """Client autenticado como admin via JWT."""
    from rest_framework.test import APIClient
    from rest_framework_simplejwt.tokens import RefreshToken

    api_client = APIClient()
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def technician_client(client, technician_user):
    from rest_framework.test import APIClient
    from rest_framework_simplejwt.tokens import RefreshToken

    api_client = APIClient()
    refresh = RefreshToken.for_user(technician_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def manager_client(client, manager_user):
    from rest_framework.test import APIClient
    from rest_framework_simplejwt.tokens import RefreshToken

    api_client = APIClient()
    refresh = RefreshToken.for_user(manager_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def anon_client():
    from rest_framework.test import APIClient
    return APIClient()
