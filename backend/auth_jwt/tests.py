import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestLoginView:
    url = '/api/auth/login/'

    def test_login_success(self, client, admin_user):
        from rest_framework.test import APIClient
        api = APIClient()
        response = api.post(self.url, {
            'email': 'admin@test.com',
            'password': 'testpass123',
        }, format='json')
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert 'user' in response.data

    def test_login_wrong_password(self, client, admin_user):
        from rest_framework.test import APIClient
        api = APIClient()
        response = api.post(self.url, {
            'email': 'admin@test.com',
            'password': 'wrongpass',
        }, format='json')
        assert response.status_code == 400

    def test_login_nonexistent_user(self, client):
        from rest_framework.test import APIClient
        api = APIClient()
        response = api.post(self.url, {
            'email': 'nobody@test.com',
            'password': 'irrelevant',
        }, format='json')
        assert response.status_code == 400

    def test_login_missing_fields(self, client):
        from rest_framework.test import APIClient
        api = APIClient()
        response = api.post(self.url, {}, format='json')
        assert response.status_code == 400


@pytest.mark.django_db
class TestRefreshTokenView:
    url = '/api/auth/refresh/'

    def test_refresh_success(self, admin_user):
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken

        api = APIClient()
        refresh = RefreshToken.for_user(admin_user)
        response = api.post(self.url, {'refresh': str(refresh)}, format='json')
        assert response.status_code == 200
        assert 'access' in response.data

    def test_refresh_invalid_token(self):
        from rest_framework.test import APIClient
        api = APIClient()
        response = api.post(self.url, {'refresh': 'invalid.token.here'}, format='json')
        assert response.status_code == 401


@pytest.mark.django_db
class TestLogoutView:
    url = '/api/auth/logout/'

    def test_logout_success(self, admin_client, admin_user):
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(admin_user)
        response = admin_client.post(self.url, {'refresh': str(refresh)}, format='json')
        assert response.status_code == 200

    def test_logout_unauthenticated(self, anon_client):
        response = anon_client.post(self.url, {'refresh': 'any'}, format='json')
        assert response.status_code == 401
