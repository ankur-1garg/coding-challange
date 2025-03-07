from rest_framework import permissions

class IsSuperUserOrReadOnly(permissions.BasePermission):
    """Only superusers can modify orders. Others can only read."""
    
    def has_permission(self, request, view):
        return request.user.is_superuser or request.method in permissions.SAFE_METHODS
