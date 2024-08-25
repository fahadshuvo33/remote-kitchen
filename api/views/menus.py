from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from restaurants.models import Menu, MenuItem
from api.serializers.menus import MenuSerializer, MenuItemSerializer
from accounts.permissions import IsOwner, IsEmployee
from restaurants.models import Restaurant


class MenuViewSet(viewsets.ModelViewSet):
    serializer_class = MenuSerializer

    def get_permissions(self):
        """
        Determine the permissions required for the current request.

        If the request is a GET, any authenticated user can access the view.
        If the request is a POST, PUT, PATCH, or DELETE, the user must be the
        owner of the restaurant or an employee of the restaurant.
        """
        if self.request.method == "GET":
            self.permission_classes = [IsAuthenticated]
        elif self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            self.permission_classes = [IsOwner | IsEmployee]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """
        Return a queryset of Menu objects that the requesting user is allowed to see.

        If the requesting user is an employee or customer, return a queryset of
        Menus associated with the restaurant the user belongs to.

        If the requesting user is an owner, return a queryset of Menus associated
        with restaurants owned by the requesting user.

        Otherwise, return an empty queryset.
        """
        user = self.request.user
        if user.role in ["employee", "customer"]:
            return Menu.objects.filter(restaurant=user.restaurant)
        elif user.role == "owner":
            return Menu.objects.filter(restaurant__owner=user)
        return Menu.objects.none()

    def perform_create(self, serializer):
        """
        Create a new Menu object and save it to the database.

        If the requesting user is an employee, the restaurant associated with
        the menu must be the same as the restaurant the user belongs to.

        If the requesting user is an owner, the restaurant associated with the
        menu must be one of the restaurants owned by the requesting user.

        Otherwise, a PermissionDenied exception will be raised.
        """
        restaurant_id = self.request.data.get("restaurant")
        try:
            restaurant = Restaurant.objects.get(id=restaurant_id)
        except Restaurant.DoesNotExist:
            raise ValidationError("Invalid restaurant ID.")

        if self.request.user.role == "employee":
            if restaurant != self.request.user.restaurant:
                raise PermissionDenied(
                    "Employees can only create menus for their own restaurant."
                )
        elif self.request.user.role == "owner":
            if (
                self.queryset.filter(restaurant=restaurant_id).owner
                != self.request.user
            ):
                raise PermissionDenied(
                    "Owners can create menus for their own restaurants."
                )
        serializer.save()

    def perform_update(self, serializer):
        """
        Update a Menu object and save it to the database.

        If the requesting user is an employee, the restaurant associated with
        the menu must be the same as the restaurant the user belongs to.

        If the requesting user is an owner, the restaurant associated with the
        menu must be one of the restaurants owned by the requesting user.

        Otherwise, a PermissionDenied exception will be raised.
        """
        menu = self.get_object()
        if self.request.user.role == "employee":
            if self.request.user.restaurant != menu.restaurant:
                raise PermissionDenied(
                    "Employees can only update menus for their own restaurant."
                )
        elif self.request.user.role == "owner":
            if menu.restaurant.owner != self.request.user:
                raise PermissionDenied(
                    "Owners can only update menus for their associated restaurants."
                )
        serializer.save()

    def perform_destroy(self, instance):
        """
        Delete a Menu object from the database.

        If the requesting user is an employee, the restaurant associated with
        the menu must be the same as the restaurant the user belongs to.

        If the requesting user is an owner, the restaurant associated with the
        menu must be one of the restaurants owned by the requesting user.

        Otherwise, a PermissionDenied exception will be raised.
        """
        if self.request.user.role == "employee":
            if self.request.user.restaurant != instance.restaurant:
                raise PermissionDenied(
                    "Employees can only delete menus for their own restaurant."
                )
        elif self.request.user.role == "owner":
            if instance.restaurant.owner != self.request.user:
                raise PermissionDenied(
                    "Owners can only delete menus for their associated restaurants."
                )
        instance.delete()


class MenuItemViewSet(viewsets.ModelViewSet):
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        """
        Determine the permissions required for the incoming request.

        If the requesting method is GET, any authenticated user can view.
        If the requesting method is POST, PUT, PATCH, or DELETE, only employees and owners can create, update, delete.

        Returns:
            list: A list of permission objects
        """
        if self.request.method == "GET":
            self.permission_classes = [
                IsAuthenticated
            ]  # All authenticated users can view
        elif self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            self.permission_classes = [
                IsOwner | IsEmployee
            ]  # Only employees and owners can create, update, delete
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """
        Determine the queryset for the incoming request.

        If the requesting user is an employee or customer, return all menu items
        for the user's associated restaurant.

        If the requesting user is an owner, return all menu items for the user's
        associated restaurants.

        Otherwise, return an empty queryset.
        """
        user = self.request.user
        if user.role in ["employee", "customer"]:
            menu_ids = Menu.objects.filter(restaurant=user.restaurant).values_list(
                "id", flat=True
            )
            return MenuItem.objects.filter(menu__id__in=menu_ids)
        elif user.role == "owner":
            menu_ids = Menu.objects.filter(restaurant__owner=user).values_list(
                "id", flat=True
            )
            return MenuItem.objects.filter(menu__id__in=menu_ids)
        return MenuItem.objects.none()

    def perform_create(self, serializer):
        """
        Create a new MenuItem object and save it to the database.

        If the requesting user is an employee, the menu associated with
        the menu item must be the same as the restaurant the user belongs to.

        If the requesting user is an owner, the menu associated with the
        menu item must be one of the menus of the restaurants owned by the
        requesting user.

        Otherwise, a PermissionDenied exception will be raised.
        """
        menu_id = self.request.data.get("menu")
        try:
            menu = Menu.objects.get(id=menu_id)
        except Menu.DoesNotExist:
            raise ValidationError("Invalid menu ID.")
        if self.request.user.role == "employee":
            if self.request.user.restaurant != menu.restaurant:

                raise PermissionDenied(
                    "Employees can only create menu items for their own restaurant."
                )
        elif self.request.user.role == "owner":
            if menu.restaurant.owner != self.request.user:
                raise PermissionDenied(
                    "Owners can only create menu items for their associated restaurants."
                )
        serializer.save()

    def perform_update(self, serializer):
        """
        Update a MenuItem object and save it to the database.

        If the requesting user is an employee, the menu associated with
        the menu item must be the same as the restaurant the user belongs to.

        If the requesting user is an owner, the menu associated with the
        menu item must be one of the menus of the restaurants owned by the
        requesting user.

        Otherwise, a PermissionDenied exception will be raised.
        """
        item = self.get_object()
        menu = item.menu

        if self.request.user.role == "employee":
            if self.request.user.restaurant != menu.restaurant:
                raise PermissionDenied(
                    "Employees can only update menu items for their own restaurant."
                )
        elif self.request.user.role == "owner":
            if menu.restaurant.owner != self.request.user:
                raise PermissionDenied(
                    "Owners can only update menu items for their associated restaurants."
                )

        serializer.save()

    def perform_destroy(self, instance):
        """
        Delete a MenuItem object from the database.

        If the requesting user is an employee, the menu associated with
        the menu item must be the same as the restaurant the user belongs to.

        If the requesting user is an owner, the menu associated with the
        menu item must be one of the menus of the restaurants owned by the
        requesting user.

        Otherwise, a PermissionDenied exception will be raised.
        """

        menu = instance.menu
        if self.request.user.role == "employee":
            if self.request.user.restaurant != menu.restaurant:
                raise PermissionDenied(
                    "Employees can only delete menu items for their own restaurant."
                )
        elif self.request.user.role == "owner":
            if menu.restaurant.owner != self.request.user:
                raise PermissionDenied(
                    "Owners can only delete menu items for their associated restaurants."
                )
        instance.delete()
