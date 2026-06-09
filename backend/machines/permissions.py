from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsEditorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.profile in ('administrador', 'gerente', 'tecnico', 'operador')

class IsAdminManagerForDelete(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return getattr(request.user, 'profile', None) in ('administrador', 'gerente')
        return True
