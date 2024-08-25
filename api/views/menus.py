# api/views/menus.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from restaurants.models import Menu, MenuItem
from api.serializers.menus import MenuSerializer, MenuItemSerializer
from accounts.permissions import IsOwner, IsEmployee

class MenuViewSet(viewsets.ModelViewSet):
    serializer_class = MenuSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [IsAuthenticated]  
        elif self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            self.permission_classes = [IsOwner | IsEmployee]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.role in ["employee","customer"]:
            return Menu.objects.filter(restaurant=user.restaurant)
        elif user.role == "owner":
            # Owners can view menus from their restaurants
            return Menu.objects.filter(restaurant__owner=user)
        return Menu.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role == 'employee':
            # Employees can only create menus for their own restaurant
            if self.request.data.get('restaurant') == str(self.request.user.restaurant.id):
                serializer.save()
            else:
                raise PermissionDenied("Employees can only create menus for their own restaurant.")
        elif self.request.user.role == 'owner':
            serializer.save()

    def perform_update(self, serializer):
        menu = self.get_object()
        if self.request.user.role == 'employee':
            # Employees can only update menus for their own restaurant
            if self.request.user.restaurant == menu.restaurant:
                serializer.save()
            else:
                raise PermissionDenied("Employees can only update menus for their own restaurant.")
        elif self.request.user.role == 'owner':
            serializer.save()

    def perform_destroy(self, instance):
        if self.request.user.role == 'employee':
            # Employees can only delete menus for their own restaurant
            if self.request.user.restaurant == instance.restaurant:
                instance.delete()
            else:
                raise PermissionDenied("Employees can only delete menus for their own restaurant.")
        elif self.request.user.role == 'owner':
            instance.delete()

class MenuItemViewSet(viewsets.ModelViewSet):
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [IsAuthenticated]  # All authenticated users can view
        elif self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            self.permission_classes = [IsOwner | IsEmployee]  # Only employees and owners can create, update, delete
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.role in ["employee","customer"]:
            menu_ids = Menu.objects.filter(restaurant=user.restaurant).values_list('id', flat=True)
            return MenuItem.objects.filter(menu__id__in=menu_ids)
        elif user.role == "owner":
            menu_ids = Menu.objects.filter(restaurant__owner=user).values_list('id', flat=True)
            return MenuItem.objects.filter(menu__id__in=menu_ids)
        return MenuItem.objects.none()

    def perform_create(self, serializer):
        menu_id = self.request.data.get('menu')
        menu = Menu.objects.filter(id=menu_id).first()
        if not menu:
            raise PermissionDenied("Invalid menu ID.")
        if self.request.user.role == 'employee':
            if self.request.user.restaurant == menu.restaurant:
                serializer.save()
            else:
                raise PermissionDenied("Employees can only create menu items for their own restaurant.")
        elif self.request.user.role == 'owner':
            serializer.save()

    def perform_update(self, serializer):
        item = self.get_object()
        menu = item.menu
        if self.request.user.role == 'employee':
            if self.request.user.restaurant == menu.restaurant:
                serializer.save()
            else:
                raise PermissionDenied("Employees can only update menu items for their own restaurant.")
        elif self.request.user.role == 'owner':
            serializer.save()

    def perform_destroy(self, instance):
        menu = instance.menu
        if self.request.user.role == 'employee':
            if self.request.user.restaurant == menu.restaurant:
                instance.delete()
            else:
                raise PermissionDenied("Employees can only delete menu items for their own restaurant.")
        elif self.request.user.role == 'owner':
            instance.delete()
