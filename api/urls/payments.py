from django.urls import path
from api.views import payments

urlpatterns = [
    path('create-payment-intent/', views.PaymentIntentView.as_view(), name='create_payment_intent'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('user-payments/', views.UserPaymentsView.as_view(), name='user_payments'),
]