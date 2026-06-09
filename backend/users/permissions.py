from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.profile in ('administrador', 'gerente')
        )

class IsTechOrOp(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.profile in ('tecnico', 'operador')
        )

class IsViewerReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.user.profile == 'visualizador':
            return False
        return True

class IsTechOpTaskPermission(BasePermission):
    """
    Técnicos e Operadores só podem editar OS atribuídas a eles ou em aberto (assigned_to=None).
    Admins e Gerentes podem editar qualquer uma.
    Visualizadores não podem editar nada.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
            
        profile = getattr(request.user, 'profile', None)
        
        if profile in ('administrador', 'gerente'):
            return True
            
        if profile in ('tecnico', 'operador'):
            if request.method in ('PUT', 'PATCH'):
                return obj.assigned_to == request.user or obj.assigned_to is None
            if request.method == 'DELETE':
                return False
                
        return False

