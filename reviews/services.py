"""
reviews/services.py
===================
Review business logic + Place rating recompute trigger.

FIX: update_review() metodi qo'shildi — PUT/PATCH da ham
recompute_rating() chaqiriladi va review to'g'ri yangilanadi.
"""
from django.db.models import QuerySet, F
from django.db import transaction

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
        # Recompute place rating (signal da created=True bo'lganda skip qilinadi)
        PlaceService.recompute_rating(place.pk)
        return review

    @staticmethod
    @transaction.atomic
    def update_review(review: Review, rating: int, comment: str = "") -> Review:
        """
        FIX: Avval yo'q edi. PUT/PATCH da ishlatiladi.
        Rating o'zgarganda place average_rating qayta hisoblanadi.
        """
        review.rating = rating
        review.comment = comment
        review.save(update_fields=["rating", "comment", "updated_at"])
        # Signal UPDATE da o'zi chaqiradi, lekin explicit qilamiz aniqlik uchun
        # Signal allaqachon post_save da chaqiradi — bu yerda kerak emas.
        # (signal created=False ko'rganda recompute qiladi)
        return review

    @staticmethod
    @transaction.atomic
    def delete_review(review: Review) -> None:
        place_id = review.place_id
        user = review.user
        review.delete()
        user.profile.total_reviews = F("total_reviews") - 1
        user.profile.save(update_fields=["total_reviews"])
        # Signal post_delete da recompute qiladi — bu yerda kerak emas.
        # Lekin delete() signal orqali ketadi, PlaceService.recompute_rating()
        # review_deleted signal handler da chaqiriladi.
        
        
        
    