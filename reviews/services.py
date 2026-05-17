"""
reviews/services.py
===================
Review business logic + Place rating recompute trigger.
"""
from django.db.models import QuerySet
from django.db import transaction
from django.db.models import F

from places.services import PlaceService
from .models import Review


class ReviewService:

    @staticmethod
    def get_place_reviews(place_id) -> "QuerySet":
        return (
            Review.objects
            .filter(place_id=place_id, is_approved=True)
            .select_related("user", "user__profile")
            .prefetch_related("images")
            .order_by("-created_at")
        )

    @staticmethod
    @transaction.atomic
    def create_review(user, place, rating: int, comment: str = "") -> Review:
        review = Review.objects.create(
            user=user, place=place, rating=rating, comment=comment
        )
        # Update user stats
        user.profile.total_reviews = F("total_reviews") + 1
        user.profile.save(update_fields=["total_reviews"])
        # Recompute place rating
        PlaceService.recompute_rating(place.pk)
        return review

    @staticmethod
    @transaction.atomic
    def delete_review(review: Review) -> None:
        place_id = review.place_id
        user = review.user
        review.delete()
        user.profile.total_reviews = F("total_reviews") - 1
        user.profile.save(update_fields=["total_reviews"])
        PlaceService.recompute_rating(place_id)