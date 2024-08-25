from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from orders.models import Order, OrderItem
from api.serializers.orders import OrderSerializer, OrderItemSerializer
from accounts.permissions import IsCustomer, IsEmployee, IsOwner

from rest_framework.exceptions import PermissionDenied


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.request.method in ["GET"]:
            self.permission_classes = [IsAuthenticated]
        elif self.request.method in ["POST"]:
            self.permission_classes = [
                IsCustomer | IsOwner
            ]  # Customers can create orders, but typically POST is restricted.
        elif self.request.method in ["PUT", "PATCH", "DELETE"]:
            self.permission_classes = [IsOwner | IsEmployee]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.role == "customer":
            # Customers can only see their own orders
            return Order.objects.filter(customer=user)
        elif user.role == "employee":
            # Employees can see orders from their own restaurant
            return Order.objects.filter(restaurant=user.restaurant)
        elif user.role == "owner":
            # Owners can see orders from their own restaurants
            return Order.objects.filter(restaurant__owner=user)
        return Order.objects.none()

    def perform_create(self, serializer):
        # Customers can create orders but only if they are authenticated
        if self.request.user.role == "customer":
            serializer.save(customer=self.request.user)
        else:
            raise PermissionDenied("Only customers can create orders.")

    def perform_update(self, serializer):
        # Ensure only employees or owners can update orders
        if self.request.user.role in ["employee", "owner"]:
            serializer.save()
        else:
            raise PermissionDenied("Only employees and owners can update orders.")

    def perform_destroy(self, instance):
        # Ensure only employees or owners can delete orders
        if self.request.user.role in ["employee", "owner"]:
            super().perform_destroy(instance)
        else:
            raise PermissionDenied("Only employees and owners can delete orders.")


class OrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        # Filter order items based on the orders the user can see
        if user.role == "customer":
            # Customers can see order items only from their own orders
            return OrderItem.objects.filter(order__customer=user)
        elif user.role == "employee":
            # Employees can see order items from orders in their own restaurant
            return OrderItem.objects.filter(order__restaurant=user.restaurant)
        elif user.role == "owner":
            # Owners can see order items from orders in their own restaurants
            return OrderItem.objects.filter(order__restaurant__owner=user)
        return OrderItem.objects.none()
