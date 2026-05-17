"""
reviews/serializers.py
======================
ReviewImageSerializer    — gallery images inside a review
ReviewListSerializer     — compact, for place detail page
ReviewDetailSerializer   — full review with images
ReviewWriteSerializer    — create / update by authenticated user
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
    `place` is injected from the URL kwarg in the view, not the request body.
    """
    images = ReviewImageSerializer(many=True, read_only=True)

    class Meta:
        model  = Review
        fields = ["rating", "comment", "images"]

    def validate_rating(self, value):
        if value not in range(1, 6):
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def create(self, validated_data):
        # place and user injected via perform_create in the view
        return Review.objects.create(**validated_data)