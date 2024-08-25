from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from accounts.models import User
from restaurants.models import Restaurant
from api.serializers.users import CustomerSerializer , EmployeeSerializer
from accounts.permissions import (
    IsOwner,
    IsEmployee,
    IsCustomer,
)

class CustomerView(viewsets.ModelViewSet):
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

        if user.role == 'customer':
            # Customers can only access their own profile
            return User.objects.filter(id=user.id)
        elif user.role == 'employee':
            # Employees can view all customers in their own restaurant
            return User.objects.filter(restaurant=user.restaurant, role='customer')
        elif user.role == 'owner':
            # Owners can view all customers in their associated restaurants
            restaurant_ids = Restaurant.objects.filter(owner=user).values_list('id', flat=True)
            return User.objects.filter(restaurant__id__in=restaurant_ids, role='customer')
        else:
            # Default to empty queryset if the role is not recognized
            return User.objects.none()

    def perform_create(self, serializer):
        # Allow customers to create their own profile
        if self.request.user.role == 'customer':
            if self.request.user == serializer.instance:
                raise PermissionDenied("Customers cannot create a new profile for themselves. Update their existing profile instead.")
            serializer.save()
        else:
            serializer.save()

    def perform_update(self, serializer):
        # Allow customers to update only their own profile
        if self.request.user.role == 'customer' and self.request.user != serializer.instance:
            raise PermissionDenied("Customers can only update their own profile.")
        serializer.save()

    def perform_destroy(self, instance):
        # Prevent customers from deleting their own profiles
        if self.request.user == instance:
            raise PermissionDenied("Customers cannot delete their own profile.")
        super().perform_destroy(instance)

