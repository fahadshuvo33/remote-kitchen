import stripe
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from payments.models import Payment
from api.serializers.payments import PaymentSerializer
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.exceptions import ValidationError

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentIntentView(CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                amount = int(
                    serializer.validated_data["amount"] * 100
                )  # Convert to cents
                currency = serializer.validated_data["currency"]

                intent = stripe.PaymentIntent.create(
                    amount=amount,
                    currency=currency,
                    metadata={"integration_check": "accept_a_payment"},
                )

                payment = serializer.save(
                    stripe_payment_intent_id=intent.id, status="pending"
                )
                return Response(
                    {
                        "clientSecret": intent.client_secret,
                        "payment": PaymentSerializer(payment).data,
                    },
                    status=201,
                )
            else:
                raise ValidationError(serializer.errors)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class UserPaymentsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return JsonResponse({"error": "Invalid payload"}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({"error": "Invalid signature"}, status=400)

    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        handle_successful_payment(payment_intent)

    return JsonResponse({"status": "success"})


def handle_successful_payment(payment_intent):
    try:
        payment = Payment.objects.get(stripe_payment_intent_id=payment_intent["id"])
        payment.status = "succeeded"
        payment.save()
    except Payment.DoesNotExist:
        pass
