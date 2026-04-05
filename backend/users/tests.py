import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserEndpoints:
    list_create_url = '/api/users/'

    def test_list_users_as_admin(self, admin_client, admin_user, technician_user):
        response = admin_client.get(self.list_create_url)
        assert response.status_code == 200
        # Check if users are listed
        results = response.data.get('results', [])
        assert len(results) >= 2

    def test_list_users_as_technician(self, technician_client):
        # Technician should not have access to user list
        response = technician_client.get(self.list_create_url)
        assert response.status_code == 403

    def test_create_user_as_admin(self, admin_client):
        data = {
            'email': 'new_user@test.com',
            'username': 'new_user',
            'password': 'newpass123',
            'password_confirm': 'newpass123',
            'name': 'Novo Usuario',
            'cpf': '999.888.777-66',
            'system_role': 'TECHNICIAN',
            'company_role': 'OPERATOR',
        }
        response = admin_client.post(self.list_create_url, data, format='json')
        assert response.status_code == 201
        assert User.objects.filter(email='new_user@test.com').exists()

    def test_get_user_detail_self(self, technician_client, technician_user):
        url = f'/api/users/{technician_user.id}/'
        response = technician_client.get(url)
        assert response.status_code == 200
        assert response.data['email'] == technician_user.email

    def test_get_user_detail_other_forbidden(self, technician_client, admin_user):
        url = f'/api/users/{admin_user.id}/'
        response = technician_client.get(url)
        assert response.status_code == 403

    def test_update_user_self(self, technician_client, technician_user):
        url = f'/api/users/{technician_user.id}/'
        data = {'name': 'Nome Editado'}
        response = technician_client.patch(url, data, format='json')
        assert response.status_code == 200
        technician_user.refresh_from_db()
        assert technician_user.name == 'Nome Editado'

    def test_delete_user_as_admin(self, admin_client, technician_user):
        url = f'/api/users/{technician_user.id}/'
        response = admin_client.delete(url)
        assert response.status_code == 204
        assert not User.objects.filter(id=technician_user.id).exists()

    def test_delete_self_forbidden(self, admin_client, admin_user):
        url = f'/api/users/{admin_user.id}/'
        response = admin_client.delete(url)
        assert response.status_code == 400
