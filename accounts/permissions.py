from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        """
        Check if the user is an owner.

        Args:
            request (Request): The incoming request.
            view (View): The view being accessed.

        Returns:
            bool: If the user is an owner.
        """
        if not request.user.is_authenticated:
            return False

        return request.user.role == "owner"


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        """
        Check if the user is an employee.

        Args:
            request (Request): The incoming request.
            view (View): The view being accessed.

        Returns:
            bool: If the user is an employee.
        """
        return request.user.is_authenticated and request.user.role == "employee"

    def has_object_permission(self, request, view, obj):
        """
        Check if the user is the same as the object.

        Args:
            request (Request): The incoming request.
            view (View): The view being accessed.
            obj (User): The object being accessed.

        Returns:
            bool: If the user is the same as the object.
        """
        return obj == request.user


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        """
        Check if the user is a customer.

        Args:
            request (Request): The incoming request.
            view (View): The view being accessed.

        Returns:
            bool: If the user is a customer.
        """
        return request.user.is_authenticated and request.user.role == "customer"

    def has_object_permission(self, request, view, obj):
        """
        Check if the user is the same as the object.

        Args:
            request (Request): The incoming request.
            view (View): The view being accessed.
            obj (User): The object being accessed.

        Returns:
            bool: If the user is the same as the object.
        """
        return request.user == obj


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        """
        Check if the user is a super admin.

        Args:
            request (Request): The incoming request.
            view (View): The view being accessed.

        Returns:
            bool: If the user is a super admin.
        """
        return request.user.is_authenticated and request.user.is_superuser
