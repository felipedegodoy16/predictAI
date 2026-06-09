from rest_framework import permissions

class IsAdminOrRelatedOrReadOnly(permissions.BasePermission):
    """
    Permite leitura a todos autenticados.
    Permite mover card no Kanban (apenas campo 'status') a qualquer autenticado.
    Permite edicao completa apenas ao Admin ou quem abriu a OS.
    """
    def has_object_permission(self, request, view, obj):
        # Operacoes de leitura sao permitidas para qualquer requisicao segura
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.profile == 'administrador':
            return True

        if hasattr(obj, 'opened_by') and obj.opened_by == request.user:
            return True

        # Permite PATCH apenas com o campo 'status' (mover card no Kanban)
        if request.method == 'PATCH':
            allowed_only_status = set(request.data.keys()) <= {'status'}
            if allowed_only_status:
                return True

        return False
