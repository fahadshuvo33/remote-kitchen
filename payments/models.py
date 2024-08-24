from django.db import models

# import stripe

# stripe.api_key = "YOUR_STRIPE_SECRET_KEY"
PAYMENT_CHOICES = [
    ("card", "Card"),
    ("bank_transfer", "Bank Transfer"),
]


class Payment(models.Model):
    # order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_id = models.CharField(max_length=255)
