from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.orders import *

# Initialize the router
router = DefaultRouter()

# Register viewsets with the router
router.register(r"my-orders", MyOrderViewSet, basename="my-order")
router.register(r"my-order-items", MyOrderItemViewSet, basename="my-order-item")
router.register(r"all-orders", AllOrderViewSet, basename="all-order")
router.register(r"all-order-items", AllOrderItemViewSet, basename="all-order-item")

# Define URL patterns
urlpatterns = [
    path("", include(router.urls)),
]
