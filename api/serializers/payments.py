from rest_framework import serializers
from payments.models import Payment
from orders.models import Order


class PaymentSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())

    class Meta:
        model = Payment
        fields = "__all__"
