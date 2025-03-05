from rest_framework import permissions

class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow:
    - Superusers to perform CRUD operations
    - Authenticated users to view products
    """
    
    def has_permission(self, request, view):
        # Allow authenticated users to view
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        # Allow only superusers to modify
        return request.user and request.user.is_superuser