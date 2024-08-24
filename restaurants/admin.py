from django.contrib import admin
from .models import Restaurant, Menu, MenuItem
from orders.models import Order


class RestaurantAdmin(admin.ModelAdmin):
    # Custom admin for owners
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == "owner":
            return qs.filter(owner=request.user)
        return qs

    def has_module_permission(self, request):
        return request.user.role in ["owner", "employee"]

    def has_view_permission(self, request, obj=None):
        if request.user.role == "owner":
            return obj is None or obj.owner == request.user
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.role == "owner":
            return obj is None or obj.owner == request.user
        return False

    def has_delete_permission(self, request, obj=None):
        if request.user.role == "owner":
            return obj is None or obj.owner == request.user
        return False


admin.site.register(Restaurant)
admin.site.register(Menu)
admin.site.register(MenuItem)
# admin.site.register(Order, OrderAdmin)
