import uuid
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from machines.models import Machine


class MachineApiKeyAuthentication(BaseAuthentication):
    """Autenticacao via API Key da maquina.

    A chave deve ser enviada no header: X-API-Key: <uuid>

    Retorna a instancia da maquina como 'user' autenticado
    para que as views possam acessar request.auth (a maquina).
    """

    def authenticate(self, request):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return None  # Deixa outros backends de autenticacao tentarem

        # Validar formato UUID antes de consultar o banco
        try:
            uuid.UUID(str(api_key))
        except ValueError:
            raise AuthenticationFailed('API Key invalida: formato incorreto.')

        try:
            machine = Machine.objects.select_related('created_by').get(api_key=api_key)
        except Machine.DoesNotExist:
            raise AuthenticationFailed('API Key invalida: maquina nao encontrada.')

        if machine.status == Machine.Status.INACTIVE:
            raise AuthenticationFailed(
                f'Maquina "{machine.name}" esta inativa. Ative-a antes de enviar leituras.'
            )

        return (machine, api_key)

    def authenticate_header(self, request):
        return 'X-API-Key'
