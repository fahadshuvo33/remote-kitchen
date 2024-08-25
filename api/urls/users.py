from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.users import CustomerView, EmployeeView, OwnerView

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"customers", CustomerView, basename="customer")
router.register(r"employees", EmployeeView, basename="employee")
router.register(r"owners", OwnerView, basename="owner")

urlpatterns = [
    path("", include(router.urls)),
]
