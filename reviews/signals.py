"""
reviews/signals.py
==================
Post-save / post-delete signals that keep Place.average_rating and
Place.review_count in sync whenever a Review is created or deleted.

NOTE: These signals are a safety net for direct ORM writes
(e.g. admin panel, management commands, bulk operations).

FIX: post_save signal faqat UPDATE da ishga tushadi (created=False).
CREATE holatida ReviewService.create_review() allaqachon
PlaceService.recompute_rating() ni chaqiradi — double recompute oldini olish uchun.
"""

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from places.services import PlaceService
from .models import Review


@receiver(post_save, sender=Review)
def review_saved(sender, instance: Review, created: bool, **kwargs) -> None:
    """
    Faqat UPDATE da recompute qilinadi.
    CREATE da ReviewService.create_review() allaqachon chaqirgan — skip.
    """
    if not created:
        PlaceService.recompute_rating(instance.place_id)


@receiver(post_delete, sender=Review)
def review_deleted(sender, instance: Review, **kwargs) -> None:
    """Recompute place rating after a review is hard-deleted."""
    PlaceService.recompute_rating(instance.place_id)