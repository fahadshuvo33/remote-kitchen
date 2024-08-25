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
    def has_permission(self, request, view):

        return request.user.is_authenticated and request.user.role == 'employee'
    
    def has_object_permission(self, request, view, obj):
        return obj == request.user


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'customer'

    def has_object_permission(self, request, view, obj):
        return request.user == obj


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ["GET"]:
            user = request.user
            
            if user.role == "owner":
                return True
            
            if user.role == "customer" and obj == user:
                return True
            
            if user.role == "employee" and obj.role == "customer":
                return obj.restaurant == user.restaurant
            
            return False

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


class IsOwnerCreatingEmployee(BasePermission):
    """
    Allows creation of employee users only if the request user is an owner.
    """
    def has_permission(self, request, view):
        if request.method == "POST":
            return request.user.is_authenticated and request.user.role == "owner" and request.data.get('role') == 'employee'
        return True


class IsOwnerDeleting(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == "owner" and obj.owner == request.user:
            return True
        return False
