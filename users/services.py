"""
users/services.py
=================
Business logic kept out of views and serializers.
"""

from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class UserService:

    @staticmethod
    def get_user_queryset():
        return User.objects.select_related("profile").filter(is_active=True)

    @staticmethod
    @transaction.atomic
    def deactivate_user(user) -> None:
        user.is_active = False
        user.save(update_fields=["is_active"])