from rest_framework import permissions

class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow superusers to edit/create.
    Regular authenticated users can view.
    """
    
    def has_permission(self, request, view):
        # Allow all authenticated users to view
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        # Only allow superusers to edit/create
        return request.user and request.user.is_superuser