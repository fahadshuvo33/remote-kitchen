from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from accounts.models import User
from restaurants.models import Restaurant
from api.serializers.users import (
    CustomerSerializer,
    EmployeeSerializer,
    OwnerSerializer,
)
from accounts.permissions import IsOwner, IsEmployee, IsCustomer, IsSuperAdmin


class CustomerView(viewsets.ModelViewSet):
    """
    API endpoint that allows customers to be viewed or edited.
    """

    serializer_class = CustomerSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [IsCustomer | IsOwner | IsEmployee]
        elif self.request.method in ["POST", "PUT", "PATCH"]:
            self.permission_classes = [IsOwner | IsCustomer]
        elif self.request.method == "DELETE":
            self.permission_classes = [IsOwner]
        else:
            self.permission_classes = []

        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """
        Restrict the returned users based on the requesting user's role and associated restaurant.
        """
        user = self.request.user

        if user.role == "customer":
            # Customers can only access their own profile
            return User.objects.filter(id=user.id)
        elif user.role == "employee":
            # Employees can view all customers in their own restaurant
            return User.objects.filter(restaurant=user.restaurant, role="customer")
        elif user.role == "owner":
            # Owners can view all customers in their associated restaurants
            restaurant_ids = Restaurant.objects.filter(owner=user).values_list(
                "id", flat=True
            )
            return User.objects.filter(
                restaurant__id__in=restaurant_ids, role="customer"
            )
        else:
            # Default to empty queryset if the role is not recognized
            return User.objects.none()

    def perform_create(self, serializer):
        # Allow customers to create their own profile
        if self.request.user.role == "customer":
            if self.request.user == serializer.instance:
                raise PermissionDenied(
                    "Customers cannot create a new profile for themselves. Update their existing profile instead."
                )
            serializer.save()
        else:
            serializer.save()

    def perform_update(self, serializer):
        # Allow customers to update only their own profile
        if (
            self.request.user.role == "customer"
            and self.request.user != serializer.instance
        ):
            raise PermissionDenied("Customers can only update their own profile.")
        serializer.save()

    def perform_destroy(self, instance):
        # Prevent customers from deleting their own profiles
        if self.request.user == instance:
            raise PermissionDenied("Customers cannot delete their own profile.")
        super().perform_destroy(instance)


class EmployeeView(viewsets.ModelViewSet):
    """
    API endpoint that allows employees to be viewed or edited."""

    serializer_class = EmployeeSerializer

    def get_permissions(self):
        if self.request.method in ["GET", "POST", "PUT"]:
            self.permission_classes = [IsEmployee | IsOwner]
        elif self.request.method == "DELETE":
            self.permission_classes = [IsOwner]
        else:
            self.permission_classes = []
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        queryset = User.objects.all()
        user = self.request.user
        if user.role == "employee":
            return queryset.filter(id=user.id)
        elif user.role == "owner":
            restaurants_ids = Restaurant.objects.filter(owner=user).values_list(
                "id", flat=True
            )
            return User.objects.filter(restaurant__id__in=restaurant_ids)
        else:
            return User.objects.none()

    def perform_create(self, serializer):

        if self.request.user.role == "employee":
            raise PermissionDenied("Employees are not allowed to create new users.")
        serializer.save()

    def perform_update(self, serializer):

        if (
            self.request.user.role == "employee"
            and self.request.user != serializer.instance
        ):
            raise PermissionDenied("Employees can only update their own profile.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user == instance:
            raise PermissionDenied("Employees cannot delete their own profile.")
        super().perform_destroy(instance)


class OwnerView(viewsets.ModelViewSet):
    """
    API endpoint that allows owners to be viewed or edited."""

    serializer_class = OwnerSerializer

    def get_permissions(self):
        if self.request.method in ["GET", "PUT"]:
            self.permission_classes = [IsSuperAdmin | IsOwner]
        elif self.request.method in ["POST", "DELETE"]:
            self.permission_classes = [IsSuperAdmin]
        else:
            self.permission_classes = []
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.isAdmin:
            return User.objects.all()
        elif user.role == "owner":
            return User.objects.filter(id=user.id)
        else:
            return User.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role == "owner":
            raise PermissionDenied("Owners are not allowed to create new users.")
        serializer.save()
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        if (
            self.request.user.role == "owner"
            and self.request.user != serializer.instance
        ):
            raise PermissionDenied("Owners can only update their own profile.")
        serializer.save()
        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        if self.request.user == instance:
            raise PermissionDenied("Owners cannot delete their own profile.")
        super().perform_destroy(instance)
