from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrAdmin(BasePermission):
    """
    Разрешает безопасные методы всем,
    а небезопасные — только автору объекта или admin.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        user = request.user
        if not user.is_authenticated:
            return False

        if user.is_staff or user.role == 'admin':
            return True

        return obj.author == user


class IsAdmin(BasePermission):
    """
    Разрешает доступ только пользователям с ролью admin (или is_staff).
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        return user.is_staff or user.role == 'admin'
