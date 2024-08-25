
from django.db import models
from django.conf import settings


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE)  # ForeignKey to Order
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)  # Ensuring uniqueness
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} for Order {self.order.id} by {self.user}"


