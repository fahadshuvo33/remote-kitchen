from django.urls import path

from api.views.users import UserView

urlpatterns = [
    path("users/", UserView.as_view()),
    # path("users/<int:pk>/", UserDetailView.as_view()),
]
