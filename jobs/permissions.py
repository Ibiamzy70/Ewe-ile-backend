from rest_framework import permissions

class IsOwnerOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user and request.user.is_staff:
            return True
        if hasattr(obj, "owner"):
            return obj.owner == request.user
        if hasattr(obj, "applicant"):
            return obj.applicant == request.user
        return False
