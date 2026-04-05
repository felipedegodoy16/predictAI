from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.system_role == 'ADMIN'
        )


class IsAdminOrTechnician(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.system_role in ('ADMIN', 'TECHNICIAN')
        )


class IsAdminOrSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.system_role == 'ADMIN' or request.user == obj)
        )


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.system_role == 'MANAGER'
        )


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.system_role == 'ADMIN'
