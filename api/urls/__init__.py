from django.urls import path, include


urlpatterns = [
    path("", include("api.urls.customers")),
    path("", include("api.urls.employees")),
    path("", include("api.urls.orders")),
    path("", include("api.urls.restaurants")),
]
