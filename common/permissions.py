"""
common/permissions.py
=====================
Reusable DRF permission classes shared across all apps.
"""

from rest_framework.permissions import BasePermission, IsAuthenticatedOrReadOnly, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """Full access for admin; read-only for everyone else."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_staff or request.user.role == "admin"
        )


class IsOwnerOrAdmin(BasePermission):
    """Object-level: owner or admin can write; everyone can read."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if request.user.is_authenticated and (
            request.user.is_staff or request.user.role == "admin"
        ):
            return True
        # Support both user FK and direct user model
        owner = getattr(obj, "user", None) or getattr(obj, "created_by", None)
        return owner == request.user


class IsVerifiedUser(BasePermission):
    """Only email-verified users may write."""

    message = "Email verification required."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_verified


class IsStaffOrBusinessOwner(BasePermission):
    """Staff or business_owner role required for write operations."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_staff
            or request.user.role in ("admin", "business_owner")
        )