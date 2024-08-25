from rest_framework import serializers
from accounts.models import User


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = [
            "created_at",
            "updated_at",
            "last_login",
            "is_superuser",
            "is_staff",
            "is_active",
            "date_joined",
            "groups",
            "user_permissions",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_restaurant(self, value):
        if self.initial_data.get("role") == "customer" and value is None:
            raise serializers.ValidationError(
                f"A restaurant must be assigned for the role : {self.initial_data.get('role')}."
            )
        return value


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = [
            "created_at",
            "updated_at",
            "last_login",
            "is_superuser",
            "is_staff",
            "is_active",
            "date_joined",
            "groups",
            "user_permissions",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_restaurant(self, value):
        if self.initial_data.get("role") == "employee" and value is None:
            raise serializers.ValidationError(
                f"A restaurant must be assigned for the role : {self.initial_data.get('role')}."
            )
        return value


class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = [
            "created_at",
            "updated_at",
            "last_login",
            "is_superuser",
            "is_staff",
            "is_active",
            "date_joined",
            "groups",
            "user_permissions",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_restaurant(self, value):
        if self.initial_data.get("role") == "owner" and value is not None:
            raise serializers.ValidationError(
                f"Cannot assign a restaurant for the role : {self.initial_data.get('role')}."
            )
        return value
