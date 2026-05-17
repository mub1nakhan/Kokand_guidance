"""
users/views.py
==============
Endpoints:
  POST   /auth/register/           RegisterView
  POST   /auth/change-password/    ChangePasswordView
  GET    /users/me/                CurrentUserView
  PUT    /users/me/                CurrentUserView
  GET    /users/<id>/              UserPublicDetailView
"""

from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsOwnerOrAdmin
from .serializers import (
    ChangePasswordSerializer,
    RegisterSerializer,
    UserDetailSerializer,
    UserPublicSerializer,
)
from .services import UserService

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """POST /auth/register/ — public"""
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserDetailSerializer(user, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class ChangePasswordView(APIView):
    """POST /auth/change-password/ — authenticated"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password updated successfully."})


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """GET / PUT / PATCH /users/me/ — owner only"""
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return UserService.get_user_queryset().get(pk=self.request.user.pk)


class UserPublicDetailView(generics.RetrieveAPIView):
    """GET /users/<id>/ — public profile"""
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "id"

    def get_queryset(self):
        return UserService.get_user_queryset()