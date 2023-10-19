from rest_framework.permissions import BasePermission

class OrgadminRequired(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role_priv == "org_admin"
    

class SuperadminRequired(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role_priv == "super_admin"
