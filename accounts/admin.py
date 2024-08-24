from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class UserAdmin(BaseUserAdmin):
    list_filter = ("role", "restaurant")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == "owner":
            # Only return users associated with the owner's restaurant
            return qs.filter(restaurant=request.user.restaurant).exclude(role="owner")
        return qs

    def has_module_permission(self, request):
        return request.user.is_superuser or request.user.role == "owner"

    def has_change_permission(self, request, obj=None):
        # Prevent owners from editing other owners or employees in other restaurants
        if obj and request.user.role == "owner":
            if obj.restaurant != request.user.restaurant or obj.role == "owner":
                return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        # Prevent owners from deleting other owners or employees in other restaurants
        if obj and request.user.role == "owner":
            if obj.restaurant != request.user.restaurant or obj.role == "owner":
                return False
        return super().has_delete_permission(request, obj)

    def has_view_permission(self, request, obj=None):
        # Allow owners to view only users within their restaurant
        if request.user.role == "owner" and obj:
            return obj.restaurant == request.user.restaurant and obj.role != "owner"
        return super().has_view_permission(request, obj)


admin.site.register(User)
