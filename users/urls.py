from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
 
from .views import (
    RegisterView,
    ChangePasswordView,
    CurrentUserView,
    UserPublicDetailView,
)
 
# Auth URL'lari ham shu yerda — users app o'z tokenlarini boshqaradi
auth_urlpatterns = [
    path("register/",        RegisterView.as_view(),        name="auth-register"),
    path("login/",           TokenObtainPairView.as_view(), name="auth-login"),
    path("token/refresh/",   TokenRefreshView.as_view(),    name="auth-token-refresh"),
    path("change-password/", ChangePasswordView.as_view(),  name="auth-change-password"),
]
 
urlpatterns = [
    path("me/",        CurrentUserView.as_view(),      name="user-me"),
    path("<uuid:id>/", UserPublicDetailView.as_view(), name="user-detail"),
]