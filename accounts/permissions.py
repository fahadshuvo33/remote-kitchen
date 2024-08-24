from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    """
    Permission class to check if the user is the owner.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return request.user.role == "owner"


class IsEmployee(BasePermission):
    """
    Permission class to check if the user is an employee.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return request.user.role == "employee"


class IsCustomer(BasePermission):
    """
    Permission class to check if the user is a customer.
    """

    def has_permission(self, request, view):

        if not request.user.is_authenticated:
            return False

        return request.user.role == "customer"


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ["GET"]:
            return obj.owner == request.user or request.user.role == "admin"
        return obj.owner == request.user


class IsNotOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.role != "owner"


class IsEmployeeOfRestaurant(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == "employee":
            return obj.restaurant == request.user.restaurant
        return True


class IsOwnerOfUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.role == "employee":
            return obj.owner == request.user
        return True


class IsOwnerCreatingUser(BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return request.user.role == "owner"
        return True


class IsOwnerOfUserToDelete(BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.role == "owner":
            return False
        if request.user.role == "owner" and obj.owner == request.user:
            return True
        return False
