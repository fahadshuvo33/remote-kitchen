from django.urls import path
from api.views.payments import PaymentIntentView, UserPaymentsView, stripe_webhook

urlpatterns = [
    path(
        "create-payment-intent/",
        PaymentIntentView.as_view(),
        name="create_payment_intent",
    ),
    path("webhook/", stripe_webhook, name="stripe_webhook"),
    path("user-payments/", UserPaymentsView.as_view(), name="user_payments"),
]
