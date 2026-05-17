"""
users/serializers.py
====================
All user-facing serializers: registration, login response, profile CRUD.

Hierarchy:
  UserProfileSerializer      — embedded in user detail responses
  UserPublicSerializer       — safe public view (no email/phone)
  UserDetailSerializer       — owner/admin full view
  RegisterSerializer         — POST /auth/register/
  ChangePasswordSerializer   — POST /auth/change-password/
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from common.serializers import BaseModelSerializer
from .models import UserProfile

User = get_user_model()


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = UserProfile
        fields = [
            "avatar", "bio", "phone", "language",
            "location", "website",
            "total_reviews", "total_favorites",
        ]
        read_only_fields = ["total_reviews", "total_favorites"]


# ---------------------------------------------------------------------------
# Public (safe for other users to see)
# ---------------------------------------------------------------------------

class UserPublicSerializer(serializers.ModelSerializer):
    """Minimal representation — shown in review/guide cards."""
    profile = UserProfileSerializer(read_only=True)
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model  = User
        fields = ["id", "display_name", "role", "is_verified", "profile"]


# ---------------------------------------------------------------------------
# Owner / admin detail
# ---------------------------------------------------------------------------

class UserDetailSerializer(serializers.ModelSerializer):
    """Full user detail — only accessible by the owner or admin."""
    profile = UserProfileSerializer()
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model  = User
        fields = [
            "id", "email", "full_name", "display_name",
            "role", "is_verified", "is_active",
            "date_joined", "profile",
        ]
        read_only_fields = ["id", "email", "role", "is_verified", "is_active", "date_joined"]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})
        # Update User fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save(update_fields=list(validated_data.keys()) or ["full_name"])

        # Update nested Profile
        profile = instance.profile
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label="Confirm password")

    class Meta:
        model  = User
        fields = ["email", "full_name", "password", "password2"]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user)
        return user


# ---------------------------------------------------------------------------
# Change password
# ---------------------------------------------------------------------------

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save(update_fields=["password"])
        return user