from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.orders import OrderViewSet, OrderItemViewSet

# Initialize the router
router = DefaultRouter()

# Register viewsets with the router
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='order-item')

# Define URL patterns
urlpatterns = [
    path('', include(router.urls)),  # Include the router's URLs
]
