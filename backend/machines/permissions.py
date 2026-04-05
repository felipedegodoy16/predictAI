from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrTechnicianOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.system_role in ('ADMIN', 'TECHNICIAN')


class IsAdminForDelete(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return request.user.system_role == 'ADMIN'
        return True
