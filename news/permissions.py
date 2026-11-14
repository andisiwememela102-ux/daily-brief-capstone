"""Role-based access rules shared by the REST API views."""

from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import User

class IsReaderOrStaffRole(BasePermission):
    """Require authentication for API resources shared by newsroom roles."""

    def has_permission(self, request, view):
        """Allow the request only when it has an authenticated user."""
        return bool(request.user and request.user.is_authenticated)

class ArticleRolePermission(BasePermission):
    """Apply role rules to article creation, editing, and deletion."""

    def has_permission(self, request, view):
        """Check whether the user's role permits this request method."""
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if request.method == 'POST':
            return user.role == User.Role.JOURNALIST
        return user.role in (User.Role.EDITOR, User.Role.JOURNALIST)

    def has_object_permission(self, request, view, obj):
        """Allow writes by editors or by the journalist who owns the article."""
        if request.method in SAFE_METHODS:
            return True
        if request.user.role == User.Role.EDITOR:
            return True
        return obj.author_id == request.user.id

class IsEditor(BasePermission):
    """Restrict an API action to authenticated editors."""

    def has_permission(self, request, view):
        """Return whether the authenticated user has the editor role."""
        return bool(request.user and request.user.is_authenticated and request.user.role == User.Role.EDITOR)
