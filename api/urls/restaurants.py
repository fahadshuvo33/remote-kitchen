from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.restaurants import RestaurantViewSet

router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet, basename='restaurant')

urlpatterns = [
    path('', include(router.urls)),
]
