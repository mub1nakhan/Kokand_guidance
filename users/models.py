"""
users/models.py
===============
Authentication and profile layer for the Kokand Tourism Platform.

Design decisions:
  - AbstractUser extended: keeps Django auth machinery intact (groups, permissions,
    password hashing, etc.) while swapping username → email.
  - UserProfile separated from CustomUser: auth fields stay lean; profile is
    extended without touching the auth table (better for JWT token payloads).
  - Role-based: tourist / guide / business_owner / admin — drives permission logic
    in permissions.py without needing custom permission objects for simple cases.
  - OneToOneField with select_related("profile") covers 99 % of API serialisation.
"""

from __future__ import annotations

import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

from common.models import BaseModel


# ---------------------------------------------------------------------------
# Upload paths
# ---------------------------------------------------------------------------

def avatar_upload_path(instance: "UserProfile", filename: str) -> str:
    return f"users/{instance.user.id}/avatar/{filename}"


# ---------------------------------------------------------------------------
# Choices
# ---------------------------------------------------------------------------

class UserRole(models.TextChoices):
    TOURIST        = "tourist",        _("Tourist")
    GUIDE          = "guide",          _("Guide")
    BUSINESS_OWNER = "business_owner", _("Business Owner")
    ADMIN          = "admin",          _("Admin")


class LanguageCode(models.TextChoices):
    UZBEK   = "uz", _("Uzbek")
    RUSSIAN = "ru", _("Russian")
    ENGLISH = "en", _("English")


# ---------------------------------------------------------------------------
# Custom manager
# ---------------------------------------------------------------------------

class CustomUserManager(BaseUserManager):
    """Email-based authentication manager."""

    def _create_user(
        self, email: str, password: str | None, **extra_fields
    ) -> "CustomUser":
        if not email:
            raise ValueError(_("Email address is required."))
        email = self.normalize_email(email)
        user: CustomUser = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self, email: str, password: str | None = None, **extra_fields
    ) -> "CustomUser":
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(
        self, email: str, password: str | None = None, **extra_fields
    ) -> "CustomUser":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self._create_user(email, password, **extra_fields)


# ---------------------------------------------------------------------------
# CustomUser
# ---------------------------------------------------------------------------

class CustomUser(AbstractUser):
    """
    Platform user model — email replaces username as the login credential.

    Inherits from AbstractUser (not BaseModel) to preserve Django's auth
    internals. UUID PK is added explicitly.

    Settings requirement:
        AUTH_USER_MODEL = "users.CustomUser"
    """

    # Override PK
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Remove username; use email
    username = None  # type: ignore[assignment]
    email = models.EmailField(
        unique=True,
        db_index=True,
        verbose_name=_("Email address"),
    )

    full_name = models.CharField(max_length=255, blank=True, verbose_name=_("Full name"))

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.TOURIST,
        db_index=True,
        verbose_name=_("Role"),
    )
    is_verified = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Verified"),
        help_text=_("Email address has been verified."),
    )

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = CustomUserManager()  # type: ignore[assignment]

    class Meta:
        verbose_name        = _("User")
        verbose_name_plural = _("Users")
        ordering            = ["-date_joined"]
        indexes = [
            models.Index(fields=["email", "is_active"], name="idx_user_email_active"),
            models.Index(fields=["role", "is_verified"],  name="idx_user_role_verified"),
        ]

    def __str__(self) -> str:
        return self.email

    @property
    def display_name(self) -> str:
        return self.full_name or self.email.split("@")[0]

    @property
    def is_guide(self) -> bool:
        return self.role == UserRole.GUIDE

    @property
    def is_business_owner(self) -> bool:
        return self.role == UserRole.BUSINESS_OWNER


# ---------------------------------------------------------------------------
# UserProfile
# ---------------------------------------------------------------------------

class UserProfile(BaseModel):
    """
    Extended profile data — kept separate from CustomUser for clean JWT payloads
    and independent migration cadence.

    Always fetched via: user.profile (OneToOne reverse)
    Serialiser: use select_related("profile") on CustomUser querysets.
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name=_("User"),
    )
    avatar = models.ImageField(
        upload_to=avatar_upload_path,
        blank=True,
        null=True,
        verbose_name=_("Avatar"),
    )
    bio = models.TextField(blank=True, verbose_name=_("Bio"))
    phone = models.CharField(
        max_length=20,
        blank=True,
        db_index=True,
        verbose_name=_("Phone"),
    )
    language = models.CharField(
        max_length=5,
        choices=LanguageCode.choices,
        default=LanguageCode.UZBEK,
        verbose_name=_("Preferred language"),
    )

    # Social / discovery
    location = models.CharField(max_length=255, blank=True, verbose_name=_("Home location"))
    website  = models.URLField(max_length=255, blank=True, verbose_name=_("Website"))

    # Stats (denormalised for fast API reads)
    total_reviews   = models.PositiveIntegerField(default=0, verbose_name=_("Total reviews"))
    total_favorites = models.PositiveIntegerField(default=0, verbose_name=_("Total favorites"))

    class Meta:
        verbose_name        = _("User profile")
        verbose_name_plural = _("User profiles")
        ordering            = ["-created_at"]

    def __str__(self) -> str:
        return f"Profile({self.user.email})"