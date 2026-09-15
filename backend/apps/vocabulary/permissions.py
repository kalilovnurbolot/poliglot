from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """System objects (owner is None) are read-only for everyone; custom objects
    can only be edited or deleted by their owner."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner_id == request.user.id
