# api/serializers/menus.py
from rest_framework import serializers
from restaurants.models import Menu, MenuItem

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']  # These fields are auto-managed

class MenuSerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, read_only=True)  # Nested serialization

    class Meta:
        model = Menu
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']  # These fields are auto-managed
