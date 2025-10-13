from . import views
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    path("register/", views.RegisterUserView.as_view(), name="register_user"),
    path("login/", views.UserLoginView.as_view(), name="login_user"),
    path("profile/", views.UserProfileView.as_view(), name="user_profile"),
]