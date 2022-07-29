from rest_framework import permissions

from users.models import User


class IsSelf(permissions.BasePermission):
    '''
    Уровень доступа: клиент
    '''
    edit_methods = ("GET", "POST", "PUT", "PATCH", "DELETE")

    def has_permission(self, request, view):
        if not request.user.is_active:
            return False

        if request.user.is_authenticated and request.method in self.edit_methods:
            return True
        elif request.user.is_authenticated and request.user.role == User.is_manager:
            return True
        elif request.user.is_authenticated and (request.user.is_superuser or request.user.role == User.is_crm_admin):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return True
        elif request.user.is_authenticated and request.user.role == User.is_manager:
            return True
        elif request.user.is_authenticated and (request.user.is_superuser or request.user.role == User.is_crm_admin):
            return True
        return False


class IsManager(permissions.BasePermission):
    '''
    Уровень доступа: менеджер
    Менеджер расширяет возможности клиента
    Менеджер видет полные модели, имеет возможность читать записи пользователей, 
    также имеет право создавать записи своим пользователям и изменять их
    '''
    def has_permission(self, request, view):
        if not request.user.is_active:
            return False

        if request.user.is_authenticated and request.user.role == User.is_manager:
            return True
        elif request.user.is_authenticated and (request.user.is_superuser or request.user.role == User.is_crm_admin):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and request.user.role == User.is_manager:
            return True
        elif request.user.is_authenticated and (request.user.is_superuser or request.user.role == User.is_crm_admin):
            return True
        return False


class IsAdmin(permissions.BasePermission):
    '''
    Уровень доступа: администратор
    Администратор расширяет возможности менеджера
    Администратор имеет доступ ко всей функциональности сайта
    '''
    def has_permission(self, request, view):
        if not request.user.is_active:
            return False

        if request.user.is_authenticated and (request.user.is_superuser or request.user.role == User.is_crm_admin):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and (request.user.is_superuser or request.user.role == User.is_crm_admin):
            return True
        return False