# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views.employees import EmployeeView

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'employees', EmployeeView, basename='employee')

urlpatterns = [
    path('', include(router.urls)),
]
