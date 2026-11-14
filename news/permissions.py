from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import User

class IsReaderOrStaffRole(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

class ArticleRolePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'POST':
            return user.role == User.Role.JOURNALIST
        return user.role in (User.Role.EDITOR, User.Role.JOURNALIST)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.role == User.Role.EDITOR:
            return True
        return obj.author_id == request.user.id

class IsEditor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.EDITOR)
