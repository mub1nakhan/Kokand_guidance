"""
places/services.py
==================
All Place-related query building and business logic.
Views stay thin — they call services, not ORM directly.
"""

from django.db.models import Exists, F, OuterRef, QuerySet
from django.db import transaction

from .models import Place


class PlaceService:

    @staticmethod
    def get_list_queryset(user=None) -> QuerySet:
        """
        Base queryset for list / map endpoints.
        - select_related: prevents N+1 on category
        - prefetch_related: prevents N+1 on tags
        - annotates is_favorited if user is authenticated
        """
        from favorites.models import Favorite

        qs = (
            Place.objects
            .select_related("category")
            .prefetch_related("tags")
            .filter(is_active=True)
        )

        if user and user.is_authenticated:
            qs = qs.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(user=user, place=OuterRef("pk"))
                )
            )

        return qs

    @staticmethod
    def get_detail_queryset(user=None) -> QuerySet:
        from favorites.models import Favorite

        qs = (
            Place.objects
            .select_related("category", "created_by", "created_by__profile")
            .prefetch_related("tags", "images")
            .filter(is_active=True)
        )

        if user and user.is_authenticated:
            qs = qs.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(user=user, place=OuterRef("pk"))
                )
            )

        return qs

    @staticmethod
    def increment_view_count(place_id) -> None:
        """Race-condition-safe view counter increment."""
        Place.all_objects.filter(pk=place_id).update(view_count=F("view_count") + 1)

    @staticmethod
    @transaction.atomic
    def recompute_rating(place_id) -> None:
        """
        Called from reviews post_save / post_delete signal.
        Uses DB aggregation — never application-layer averaging.
        Now atomic to avoid race conditions.
        """
        from django.db.models import Avg, Count
        from reviews.models import Review

        agg = Review.objects.filter(
            place_id=place_id, is_approved=True
        ).aggregate(avg=Avg("rating"), count=Count("id"))

        Place.all_objects.filter(pk=place_id).update(
            average_rating=agg["avg"] or 0,
            review_count=agg["count"],
        )