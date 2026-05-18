"""
reviews/signals.py
==================
Post-save / post-delete signals that keep Place.average_rating and
Place.review_count in sync whenever a Review is created or deleted.

NOTE: These signals are a safety net.
Primary write-path already calls PlaceService.recompute_rating() inside
ReviewService.create_review() / delete_review() via @transaction.atomic.
Signals catch any direct ORM writes (e.g. admin, management commands).
"""

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from places.services import PlaceService
from .models import Review


@receiver(post_save, sender=Review)
def review_saved(sender, instance: Review, created: bool, **kwargs) -> None:
    """Recompute place rating after a review is created or updated."""
    PlaceService.recompute_rating(instance.place_id)


@receiver(post_delete, sender=Review)
def review_deleted(sender, instance: Review, **kwargs) -> None:
    """Recompute place rating after a review is hard-deleted."""
    PlaceService.recompute_rating(instance.place_id)