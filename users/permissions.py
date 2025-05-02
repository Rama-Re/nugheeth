from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class IsEmergency(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.account_type == 'emergency'


class IsNormal(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.account_type == 'normal'


class IsFamily(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.account_type == 'family'


class IsPilgrim(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.account_type == 'pilgrim'
