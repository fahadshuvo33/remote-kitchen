from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError

ROLE_CHOICES = [
    ("owner", "Owner"),
    ("employee", "Employee"),
    ("customer", "Customer"),
]


class User(AbstractUser):
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    restaurant = models.ForeignKey(
        "restaurants.Restaurant",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="users",
    )

    class Meta:
        unique_together = ("email", "restaurant")

    def __str__(self):
        return f"{self.username} role: {self.role}"

    def clean(self):
        if self.role == "owner":
            self.restaurant = None
        elif self.role in ["employee", "customer"] and self.restaurant is None:
            raise ValidationError(
                {"error": f"A restaurant must be assigned for the role {self.role}."}
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def get_restaurant(self):
        """
        Get the restaurant associated with the user based on their role.
        """
        from restaurants.models import Restaurant

        if self.role in ["employee", "customer"]:
            return self.restaurant
        elif self.role == "owner":
            # Assuming the owner can have multiple restaurants, return a list or a specific restaurant
            return Restaurant.objects.filter(user=self).first()
        return None
