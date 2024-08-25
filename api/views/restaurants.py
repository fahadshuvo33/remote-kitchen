from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from restaurants.models import Restaurant
from accounts.models import User
from api.serializers.restaurants import RestaurantSerializer
from accounts.permissions import IsOwner, IsEmployee


class RestaurantViewSet(viewsets.ModelViewSet):
    serializer_class = RestaurantSerializer

    def get_permissions(self):
        if self.request.method in ["GET"]:
            self.permission_classes = [IsAuthenticated]
        elif self.request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            self.permission_classes = [IsOwner]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.role == "owner":
            return Restaurant.objects.filter(owner=user)
        elif user.role == "employee":
            return User.objects.filter(restaurant=user.restaurant)
        else:
            return Restaurant.objects.none()

    def perform_create(self, serializer):
        if self.request.user != serializer.instance.owner:
            raise PermissionDenied(
                "You do not have permission to create a restaurant for another user."
            )
        serializer.save()
        return super().perform_create(serializer)

    def perform_update(self, serializer):
        restaurant = self.get_object()
        if self.request.user == restaurant.owner:
            serializer.save()
        else:
            raise PermissionDenied(
                "You do not have permission to update this restaurant."
            )

    def perform_destroy(self, instance):
        if self.request.user == instance.owner:
            instance.delete()
        else:
            raise PermissionDenied(
                "You do not have permission to delete this restaurant."
            )
