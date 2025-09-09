from rest_framework.permissions import BasePermission,IsAdminUser

class IsDocUser(BasePermission):
    """
    Custom permission to grant access only to users with usertype = 'doc'.
    """
    def has_permission(self, request, view):
        
        return request.user.is_authenticated and getattr(request.user, 'designation', None) == 'DOC'

class IsAdminOrDocUser(IsAdminUser):
    """
    Custom permission to grant access to admin users or users with 'designation' as 'DOC'.
    """

    def has_permission(self, request, view):
        # First, check if the user is an admin using the parent (IsAdminUser) logic
        if super().has_permission(request, view):
            return True
        
        # Then, check if the user is a doctor (has 'designation' as 'DOC')
        if request.user.is_authenticated and getattr(request.user, 'designation', None) == 'DOC':
            return True
        
        # Deny access if neither condition is met
        return False