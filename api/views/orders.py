from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from orders.models import Order, OrderItem
from api.serializers.orders import OrderSerializer, OrderItemSerializer
from accounts.permissions import IsCustomer, IsEmployee, IsOwner

from rest_framework.exceptions import PermissionDenied

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view


class MyOrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return a queryset of the orders made by the user making the request.

        :return: A queryset of Order objects
        """
        user = self.request.user
        return Order.objects.filter(customer=user)

    def perform_create(self, serializer):
        """
        Create a new Order object and save it to the database.

        If the requesting user is not the same as the customer in the
        validated data, a PermissionDenied exception will be raised.
        """

        if self.request.user != serializer.validated_data["customer"]:
            raise PermissionDenied("You cannot create an order for another user.")
        serializer.save(customer=self.request.user)

    def perform_update(self, serializer):
        """
        Update an Order object and save it to the database.

        If the requesting user is not the same as the customer in the
        validated data, a PermissionDenied exception will be raised.
        """
        if self.request.user != serializer.instance.customer:
            raise PermissionDenied("You cannot update an order for another user.")
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        """
        Delete an Order object from the database.

        If the requesting user is not the same as the customer in the
        instance, a PermissionDenied exception will be raised.
        """
        if self.request.user != instance.customer:
            raise PermissionDenied("You cannot delete an order for another user.")
        super().perform_destroy(instance)


class AllOrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsEmployee | IsOwner]
    http_method_names = ["get", "put", "patch", "delete"]

    def get_queryset(self):
        """
        Return a queryset of Order objects that the requesting user is allowed to see.

        If the requesting user is an employee, return a queryset of
        Orders associated with the restaurant the user belongs to.

        If the requesting user is an owner, return a queryset of
        Orders associated with restaurants owned by the requesting user.

        Otherwise, return an empty queryset.
        """
        if self.request.user.role == "employee":
            return Order.objects.filter(restaurant=self.request.user.restaurant)
        elif self.request.user.role == "owner":
            return Order.objects.filter(restaurant__owner=self.request.user)
        return Order.objects.none()

    def perform_update(self, serializer):
        """
        Update an Order object and save it to the database.

        If the requesting user is an employee, the restaurant associated with
        the order must be the same as the restaurant the user belongs to.

        If the requesting user is an owner, the restaurant associated with the
        order must be one of the restaurants owned by the requesting user.

        Otherwise, a PermissionDenied exception will be raised.
        """
        if self.request.user.role == "employee":
            if self.request.user.restaurant != serializer.instance.restaurant:
                raise PermissionDenied(
                    "You cannot update an order for another restaurant."
                )
        elif self.request.user.role == "owner":
            if self.request.user != serializer.instance.restaurant.owner:
                raise PermissionDenied(
                    "You cannot update an order for another restaurant."
                )
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        """
        Delete an Order object from the database.

        If the requesting user is an employee, a PermissionDenied exception will
        be raised.

        If the requesting user is an owner, the restaurant associated with the
        order must be one of the restaurants owned by the requesting user.

        Otherwise, a PermissionDenied exception will be raised.
        """
        if self.request.user.role == "employee":
            raise PermissionDenied("Employees cannot delete orders.")
        elif self.request.user.role == "owner":
            if self.request.user != instance.restaurant.owner:
                raise PermissionDenied(
                    "You cannot delete an order for another restaurant."
                )
        super().perform_destroy(instance)


class MyOrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return a queryset of all OrderItem objects associated with
        the orders of the requesting user.

        :return: A queryset of OrderItem objects
        """
        user = self.request.user
        return OrderItem.objects.filter(order__customer=user)

    def perform_create(self, serializer):
        """
        Create a new OrderItem object and save it to the database.

        If the requesting user is not the customer associated with the
        order, a PermissionDenied exception will be raised.

        :param serializer: An OrderItemSerializer object
        """
        if self.request.user != serializer.validated_data["order"].customer:
            raise PermissionDenied("You cannot create an order item for another user.")
        serializer.save(order__customer=self.request.user)

    def perform_update(self, serializer):
        """
        Update an existing OrderItem object and save it to the database.

        If the requesting user is not the customer associated with the
        order, a PermissionDenied exception will be raised.

        :param serializer: An OrderItemSerializer object
        """
        if self.request.user != serializer.instance.order.customer:
            raise PermissionDenied("You cannot update an order item for another user.")
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        """
        Delete an existing OrderItem object from the database.

        If the requesting user is not the customer associated with the
        order, a PermissionDenied exception will be raised.

        :param instance: An OrderItem object
        """
        if self.request.user != instance.order.customer:
            raise PermissionDenied("You cannot delete an order item for another user.")
        super().perform_destroy(instance)


class AllOrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [IsEmployee | IsOwner]
    http_method_names = ["get", "put", "patch", "delete"]

    def get_queryset(self):
        """
        Return a queryset of OrderItem objects that the requesting user is allowed to see.

        If the requesting user is an employee, return a queryset of OrderItems
        associated with the restaurant the user belongs to.

        If the requesting user is an owner, return a queryset of OrderItems associated
        with restaurants owned by the requesting user.

        Otherwise, return an empty queryset.
        """
        if self.request.user.role == "employee":
            return OrderItem.objects.filter(
                order__restaurant=self.request.user.restaurant
            )
        elif self.request.user.role == "owner":
            return OrderItem.objects.filter(order__restaurant__owner=self.request.user)
        return OrderItem.objects.none()

    def perform_update(self, serializer):
        """
        Update an existing OrderItem object and save it to the database.

        If the requesting user is an employee, the restaurant associated with
        the order must be the same as the restaurant the user belongs to.

        If the requesting user is an owner, the restaurant associated with the
        order must be one of the restaurants owned by the requesting user.

        Otherwise, a PermissionDenied exception will be raised.
        """
        if self.request.user.role == "employee":
            if self.request.user.restaurant != serializer.instance.order.restaurant:
                raise PermissionDenied(
                    "You cannot update an order item for another restaurant."
                )
        elif self.request.user.role == "owner":
            if self.request.user != serializer.instance.order.restaurant.owner:
                raise PermissionDenied(
                    "You cannot update an order item for another restaurant."
                )
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        """
        Delete an existing OrderItem object from the database.

        If the requesting user is an employee, raise a PermissionDenied exception.
        If the requesting user is an owner, the restaurant associated with
        the order must be one of the restaurants owned by the requesting user.

        Otherwise, a PermissionDenied exception will be raised.
        """
        if self.request.user.role == "employee":
            raise PermissionDenied("Employees cannot delete order items.")
        elif self.request.user.role == "owner":
            if self.request.user != instance.order.restaurant.owner:
                raise PermissionDenied(
                    "You cannot delete an order item for another restaurant."
                )
        super().perform_destroy(instance)
