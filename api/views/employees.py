# views.py
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


class EmployeeView(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer

    def get_permissions(self):
        if self.request.method in ["GET","POST","PUT"]:
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
            restaurants_ids = Restaurant.objects.filter(owner=user).values_list('id', flat=True)
            return User.objects.filter(restaurant__id__in=restaurant_ids)
        else : 
            return User.objects.none()

    def perform_create(self, serializer):

        if self.request.user.role == 'employee':
            raise PermissionDenied("Employees are not allowed to create new users.")
        serializer.save()

    def perform_update(self, serializer):

        if self.request.user.role == 'employee' and self.request.user != serializer.instance:
            raise PermissionDenied("Employees can only update their own profile.")
        serializer.save()

    def perform_destroy(self, instance):
        if self.request.user == instance:
            raise PermissionDenied("Employees cannot delete their own profile.")
        super().perform_destroy(instance)

