"""
favorites/models.py
===================
User bookmarks layer for the Kokand Tourism Platform.

Design decisions:
  - Plain Model (not BaseModel): Favorite is a pure join record.
    No soft-delete, no UUID — BigAutoField keeps inserts cheap at scale.
  - UniqueConstraint(user, place) enforced at DB layer: application-layer
    "toggle" logic (create-or-delete) is safe without extra locking.
  - Post-save / post-delete signals update UserProfile.total_favorites
    via F() expression to avoid race conditions.
  - No `is_active`: a bookmark is either present or deleted, never hidden.
"""

from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from places.models import Place


class Favorite(models.Model):
    """
    A user's saved bookmark of a Place.

    Toggle pattern (recommended in FavoritesService):
        obj, created = Favorite.objects.get_or_create(user=user, place=place)
        if not created:
            obj.delete()
    """

    id = models.BigAutoField(primary_key=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
        db_index=True,
        verbose_name=_("User"),
    )
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        db_index=True,
        verbose_name=_("Place"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name=_("Saved at"),
    )

    class Meta:
        verbose_name        = _("Favorite")
        verbose_name_plural = _("Favorites")
        ordering            = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "place"],
                name="unique_user_place_favorite",
            ),
        ]
        indexes = [
            models.Index(fields=["user", "created_at"], name="idx_favorite_user_timeline"),
        ]

    def __str__(self) -> str:
        return f"{self.user} ♥ {self.place.title}"