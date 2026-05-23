"""
reviews/serializers.py
======================
ReviewImageSerializer    — gallery images inside a review
ReviewListSerializer     — compact, for place detail page
ReviewDetailSerializer   — full review with images
ReviewWriteSerializer    — create / update by authenticated user
ReviewImageUploadSerializer — upload images to an existing review

FIX: ReviewWriteSerializer dan keraksiz validate_rating olib tashlandi
     (model validators allaqachon tekshiradi — DRF ularni o'zi ishlatadi).
"""

from rest_framework import serializers

from users.serializers import UserPublicSerializer
from .models import Review, ReviewImage


# ---------------------------------------------------------------------------
# Review image
# ---------------------------------------------------------------------------

class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = ReviewImage
        fields = ["id", "image", "order"]
        read_only_fields = ["id"]


# ---------------------------------------------------------------------------
# List (compact)
# ---------------------------------------------------------------------------

class ReviewListSerializer(serializers.ModelSerializer):
    user   = UserPublicSerializer(read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)
    rating_display = serializers.CharField(source="get_rating_display", read_only=True)

    class Meta:
        model  = Review
        fields = [
            "id", "user", "rating", "rating_display",
            "comment", "images", "created_at",
        ]


# ---------------------------------------------------------------------------
# Detail
# ---------------------------------------------------------------------------

class ReviewDetailSerializer(ReviewListSerializer):
    """Same as list but includes moderation flags for admin/owner."""

    class Meta(ReviewListSerializer.Meta):
        fields = ReviewListSerializer.Meta.fields + ["is_approved", "is_flagged", "updated_at"]


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

class ReviewWriteSerializer(serializers.ModelSerializer):
    """
    Authenticated user creates or updates their own review.
    `place` and `user` are injected from the view — not from request body.

    FIX: validate_rating olib tashlandi — model validators (Min/MaxValueValidator)
         DRF tomonidan avtomatik ishlatiladi, duplicate validation kerak emas.
    """
    class Meta:
        model  = Review
        fields = ["rating", "comment"]


# ---------------------------------------------------------------------------
# ReviewImage upload
# ---------------------------------------------------------------------------

class ReviewImageUploadSerializer(serializers.ModelSerializer):
    """
    POST /places/<slug>/reviews/<pk>/images/
    Foydalanuvchi o'z reviewiga rasm yuklaydi.
    `review` context orqali view dan inject qilinadi.
    """
    class Meta:
        model  = ReviewImage
        fields = ["image", "order"]

    def validate_order(self, value):
        review = self.context.get("review")
        if review and ReviewImage.objects.filter(review=review, order=value).exists():
            raise serializers.ValidationError(
                f"Bu review da {value}-tartib raqamli rasm allaqachon mavjud."
            )
        return value

    def create(self, validated_data):
        review = self.context["review"]
        return ReviewImage.objects.create(review=review, **validated_data)