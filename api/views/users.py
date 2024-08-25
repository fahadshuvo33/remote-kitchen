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
        """
        Determine the permissions required for the incoming request.

        If the request is a GET, customers, owners, and employees can view.
        If the request is a POST, anyone can create.
        If the request is a PUT or PATCH, owners and customers can update.
        If the request is a DELETE, only owners can delete.
        """
        if self.request.method == "GET":
            self.permission_classes = [IsCustomer | IsOwner | IsEmployee]
        elif self.request.method == "POST":
            self.permission_classes = []
        elif self.request.method in ["PUT", "PATCH"]:
            self.permission_classes = [IsOwner | IsCustomer]
        elif self.request.method == "DELETE":
            self.permission_classes = [IsOwner]
        else:
            self.permission_classes = []

        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """
        Determine the queryset for the incoming request.

        If the requesting user is a customer, return only the requesting user.
        If the requesting user is an employee, return all customers in the same restaurant.
        If the requesting user is an owner, return all customers in the associated restaurants.
        Otherwise, return an empty queryset.
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
        """
        Create a new User object and save it to the database.

        If the requesting user is a customer, they cannot create a new profile for themselves.
        If the requesting user is an employee, they can only create profiles for their own restaurant.
        If the requesting user is an owner, they can only create profiles for their associated restaurants.
        If the role of the created user is not customer, a PermissionDenied exception will be raised.
        """
        if self.request.user.role == "customer":
            if self.request.user == serializer.instance:
                raise PermissionDenied(
                    "Customers cannot create a new profile for themselves. Update their existing profile instead."
                )
        elif self.request.user.role == "employee":
            if self.request.user.restaurant != serializer.instance.restaurant:
                raise PermissionDenied(
                    "Employees can only create profiles for their own restaurants."
                )
        elif self.request.user.role == "owner":
            if self.request.user != serializer.instance.restaurant.owner:
                raise PermissionDenied(
                    "Owners can only create profiles for their associated restaurants."
                )
        elif serializer.validated_data.get("role") != "customer":
            raise PermissionDenied("Only customers can be created through this API")
        else:
            serializer.save()

    def perform_update(self, serializer):
        """
        Update a User object and save it to the database.

        If the requesting user is an employee, they can only update profiles for their own restaurant.
        If the requesting user is an owner, they can only update profiles for their associated restaurants.
        If the requesting user is a customer, they can only update their own profile.
        If the role of the updated user is not customer, a PermissionDenied exception will be raised.
        """
        if serializer.validated_data.get("role") != "customer":
            raise PermissionDenied("You can not update your role through this API")
        elif self.request.user.role == "employee":
            if self.request.user.restaurant != serializer.instance.restaurant:
                raise PermissionDenied(
                    "Employees can only update profiles for their own restaurants."
                )
        elif self.request.user.role == "owner":
            if self.request.user != serializer.instance.restaurant.owner:
                raise PermissionDenied(
                    "Owners can only update profiles for their associated restaurants."
                )
        elif (
            self.request.user.role == "customer"
            and self.request.user != serializer.instance
        ):
            raise PermissionDenied("Customers can only update their own profile.")
        serializer.save()

    def perform_destroy(self, instance):
        """
        Delete a User object from the database.

        If the requesting user is an owner, the restaurant associated with
        the user must be one of the restaurants owned by the requesting user.

        Otherwise, a PermissionDenied exception will be raised.
        """
        if self.request.user.role == "owner":
            if self.request.user != instance.restaurant.owner:
                raise PermissionDenied(
                    "Owners can only delete profiles for their associated restaurants."
                )

        super().perform_destroy(instance)


class EmployeeView(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer

    def get_permissions(self):
        """
        Determine the permissions required for the current request.

        If the request is a GET, PUT, or PATCH, employees and owners can access.
        If the request is a POST or DELETE, only owners can access.
        Otherwise, no permissions are required.
        """
        if self.request.method in ["GET", "PUT", "PATCH"]:
            self.permission_classes = [IsEmployee | IsOwner]
        elif self.request.method in ["POST", "DELETE"]:
            self.permission_classes = [IsOwner]
        else:
            self.permission_classes = []
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """
        Determine the queryset for the incoming request.

        If the requesting user is an employee, return only the requesting user.
        If the requesting user is an owner, return all employees in the associated restaurants.
        Otherwise, return an empty queryset.
        """
        queryset = User.objects.all()
        user = self.request.user
        if user.role == "employee":
            return queryset.filter(id=user.id)
        elif user.role == "owner":
            restaurants_ids = Restaurant.objects.filter(owner=user).values_list(
                "id", flat=True
            )
            return User.objects.filter(restaurant__id__in=restaurants_ids)
        else:
            return User.objects.none()

    def perform_create(self, serializer):
        """
        Create a new Employee object and save it to the database.

        If the requesting user is an owner, the restaurant associated with
        the employee must be one of the restaurants owned by the requesting user.

        Otherwise, a PermissionDenied exception will be raised.
        """
        if self.request.user.role == "owner":
            if self.request.user != serializer.instance.restaurant.owner:
                raise PermissionDenied(
                    "Owners can only create profiles for their associated restaurants."
                )

        serializer.save()

    def perform_update(self, serializer):
        """
        Update a User object and save it to the database.

        If the requesting user is an employee, they can only update their own profile.
        If the requesting user is an owner, they can only update profiles for their associated restaurants.
        Otherwise, a PermissionDenied exception will be raised.
        """
        if (
            self.request.user.role == "employee"
            and self.request.user != serializer.instance
        ):
            raise PermissionDenied("Employees can only update their own profile.")
        elif self.request.user.role == "owner":
            if self.request.user != serializer.instance.restaurant.owner:
                raise PermissionDenied(
                    "Owners can only update profiles for their associated restaurants."
                )
        serializer.save()

    def perform_destroy(self, instance):
        """
        Delete a User object from the database.

        If the requesting user is an owner, the restaurant associated with
        the user must be one of the restaurants owned by the requesting user.

        Otherwise, a PermissionDenied exception will be raised.
        """
        if self.request.user.role == "owner":
            if self.request.user != instance.restaurant.owner:
                raise PermissionDenied(
                    "Owners can only delete profiles for their associated restaurants."
                )
        super().perform_destroy(instance)


class OwnerView(viewsets.ModelViewSet):
    """
    API endpoint that allows owners to be viewed or edited."""

    serializer_class = OwnerSerializer

    def get_permissions(self):
        """
        Determine the permissions required for the incoming request.

        If the request is a GET, PUT, or PATCH, super admins and owners can view, update, or partially update.
        If the request is a POST, only super admins can create.
        If the request is a DELETE, only super admins can delete.
        Otherwise, no permissions are required.

        Returns:
            list: A list of permission objects
        """
        if self.request.method in ["GET", "PUT", "PATCH"]:
            self.permission_classes = [IsSuperAdmin | IsOwner]
        elif self.request.method in ["POST", "DELETE"]:
            self.permission_classes = [IsSuperAdmin]
        else:
            self.permission_classes = []
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        """
        Determine the queryset for the incoming request.

        If the requesting user is a super admin, return all owners.
        If the requesting user is an owner, return only the requesting user.
        Otherwise, return an empty queryset.
        """
        queryset = User.objects.all()
        user = self.request.user
        if user.is_superuser:
            return queryset.filter(role="owner")
        elif user.role == "owner":
            return User.objects.filter(id=user.id)
        else:
            return User.objects.none()

    def perform_create(self, serializer):
        """
        Create a new User object and save it to the database.

        If the requesting user is an owner, a PermissionDenied exception will be raised.
        Otherwise, a new User object will be created and saved to the database.
        """
        if self.request.user.role == "owner":
            raise PermissionDenied("Owners are not allowed to create new users.")
        serializer.save()
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        """
        Update a User object and save it to the database.

        If the requesting user is an owner and the user being updated is not the
        same as the requesting user, a PermissionDenied exception will be
        raised.
        Otherwise, a User object will be updated and saved to the database.
        """
        if (
            self.request.user.role == "owner"
            and self.request.user != serializer.instance
        ):
            raise PermissionDenied("Owners can only update their own profile.")
        serializer.save()
        return super().perform_update(serializer)

    def perform_destroy(self, instance):
        """
        Delete a User object from the database.

        If the requesting user is an owner, a PermissionDenied exception will be
        raised.

        Otherwise, a User object will be deleted from the database.
        """
        if self.request.user.role == "owner":
            raise PermissionDenied("Owners are not allowed to delete users.")
        super().perform_destroy(instance)
