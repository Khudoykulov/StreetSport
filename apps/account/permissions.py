from rest_framework.permissions import BasePermission
from rest_framework import permissions


class IsAdminUser(BasePermission):
    """Faqat Admin qo‘shishi mumkin"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsAdminOrOwner(BasePermission):
    """Admin va Owner qo‘shishi mumkin"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
                request.user.is_staff or (request.user.role == 'owner' and obj.owner == request.user))

    def has_permission(self, request, view):
        # Agar o‘qish (GET, HEAD, OPTIONS) bo‘lsa, ruxsat beramiz
        if request.method in permissions.SAFE_METHODS:
            return True
        # Faqat admin va owner foydalanuvchilar uchun ruxsat
        return request.user.is_authenticated and request.user.role in ['admin', 'owner']


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj == request.user or request.user.is_superuser


class IsReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.id == request.user.id
