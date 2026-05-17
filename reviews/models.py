"""
reviews/models.py
=================
User-generated review layer for the Kokand Tourism Platform.

Design decisions:
  - Plain Model (not BaseModel): reviews are high-volume transactional rows;
    BigAutoField is faster than UUID for write-heavy inserts.
  - UniqueConstraint(user, place): one review per user per place enforced at
    the DB layer — not just application-layer validation.
  - ReviewImage separated: images optional, stored independently, cleaned up
    via CASCADE when a review is deleted.
  - Post-save / post-delete signals (in reviews/signals.py) must recompute
    Place.average_rating and Place.review_count using DB aggregation, then
    save with update_fields=["average_rating", "review_count"].
"""

from __future__ import annotations

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from places.models import Place


# ---------------------------------------------------------------------------
# Upload path
# ---------------------------------------------------------------------------

def review_image_path(instance: "ReviewImage", filename: str) -> str:
    return f"reviews/{instance.review.place_id}/{instance.review_id}/{filename}"


# ---------------------------------------------------------------------------
# Choices
# ---------------------------------------------------------------------------

class RatingChoice(models.IntegerChoices):
    ONE   = 1, _("★ Poor")
    TWO   = 2, _("★★ Fair")
    THREE = 3, _("★★★ Good")
    FOUR  = 4, _("★★★★ Very Good")
    FIVE  = 5, _("★★★★★ Excellent")


# ---------------------------------------------------------------------------
# Review
# ---------------------------------------------------------------------------

class Review(models.Model):
    """
    Single user review of a place.

    Intentionally inherits from Model (not BaseModel):
      - No soft-delete: reviews are either published, flagged, or hard-deleted
        after moderation resolution.
      - BigAutoField PK is more efficient for high-frequency inserts and
        cursor-based pagination on the review feed.
    """

    id = models.BigAutoField(primary_key=True)

    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="reviews",
        db_index=True,
        verbose_name=_("Place"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        db_index=True,
        verbose_name=_("User"),
    )

    rating = models.PositiveSmallIntegerField(
        choices=RatingChoice.choices,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        db_index=True,
        verbose_name=_("Rating"),
    )
    comment = models.TextField(blank=True, verbose_name=_("Comment"))

    # Moderation
    is_approved = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Approved"),
        help_text=_("Unapproved reviews are hidden from public API."),
    )
    is_flagged = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Flagged"),
        help_text=_("Flagged by another user for moderation review."),
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        verbose_name        = _("Review")
        verbose_name_plural = _("Reviews")
        ordering            = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "place"],
                name="unique_user_place_review",
            ),
        ]
        indexes = [
            models.Index(fields=["place", "rating"],      name="idx_review_place_rating"),
            models.Index(fields=["place", "is_approved"], name="idx_review_place_approved"),
            models.Index(fields=["user",  "created_at"],  name="idx_review_user_timeline"),
        ]

    def __str__(self) -> str:
        return f"{self.user} → {self.place.title} ({self.rating}★)"


# ---------------------------------------------------------------------------
# ReviewImage
# ---------------------------------------------------------------------------

class ReviewImage(models.Model):
    """
    Optional user-uploaded images attached to a review.
    Separated from Review to keep the main table lean and allow lazy loading
    of gallery images in the mobile API.
    """

    id     = models.BigAutoField(primary_key=True)
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name="images",
        db_index=True,
        verbose_name=_("Review"),
    )
    image  = models.ImageField(upload_to=review_image_path, verbose_name=_("Image"))
    order  = models.PositiveSmallIntegerField(default=0, verbose_name=_("Order"))

    class Meta:
        verbose_name        = _("Review image")
        verbose_name_plural = _("Review images")
        ordering            = ["review", "order"]
        constraints = [
            models.UniqueConstraint(fields=["review", "order"], name="unique_review_image_order"),
        ]

    def __str__(self) -> str:
        return f"Review#{self.review_id} — image #{self.order}"