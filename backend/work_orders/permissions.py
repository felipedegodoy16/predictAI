from rest_framework import permissions

class IsAdminOrRelatedOrReadOnly(permissions.BasePermission):
    """
    Permite leitura a todos autenticados.
    Permite alteracao apenas se for Admin, criador ou usuario atribuido da OS.
    """
    def has_object_permission(self, request, view, obj):
        # Operacoes de leitura sao permitidas para qualquer requisicao segura
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.system_role == 'ADMIN':
            return True
            
        if obj.created_by == request.user:
            return True
            
        if obj.assigned_to == request.user:
            return True

        return False
