from rest_framework import serializers
from orders.models import Order, OrderItem
from restaurants.models import MenuItem
from accounts.models import User
from restaurants.models import Restaurant


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())

    class Meta:
        model = OrderItem
        fields = ["id", "menu_item", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        many=True, read_only=True
    )  # Include order items in the order response
    customer = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    restaurant = serializers.PrimaryKeyRelatedField(queryset=Restaurant.objects.all())

    class Meta:
        model = Order
        fields = [
            "id",
            "restaurant",
            "customer",
            "order_date",
            "total",
            "status",
            "items",
        ]

    def create(self, validated_data):
        items_data = self.context["request"].data.get("items", [])
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order
