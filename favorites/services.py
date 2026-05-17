"""
favorites/services.py
=====================
Toggle logic with UserProfile counter sync.
"""

from django.db import transaction
from django.db.models import F, QuerySet

from places.models import Place
from .models import Favorite


class FavoriteService:

    @staticmethod
    @transaction.atomic
    def toggle(user, place_id: str) -> dict:
        """
        Add or remove a favorite atomically.
        Returns {"status": "added" | "removed", "place_id": str(place_id)}
        """
        place = Place.objects.get(pk=place_id, is_active=True)
        fav, created = Favorite.objects.get_or_create(user=user, place=place)

        if created:
            user.profile.total_favorites = F("total_favorites") + 1
            user.profile.save(update_fields=["total_favorites"])
            return {"status": "added", "place_id": str(place_id)}
        else:
            fav.delete()
            user.profile.total_favorites = F("total_favorites") - 1
            user.profile.save(update_fields=["total_favorites"])
            return {"status": "removed", "place_id": str(place_id)}

    @staticmethod
    def get_user_favorites(user) -> "QuerySet":
        return (
            Favorite.objects
            .filter(user=user)
            .select_related("place", "place__category")
            .prefetch_related("place__tags")
            .order_by("-created_at")
        )