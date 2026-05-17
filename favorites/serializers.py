"""
favorites/serializers.py
========================
FavoriteSerializer      — list of saved places for the current user
FavoriteToggleSerializer — POST body for toggle endpoint
"""

from rest_framework import serializers

from places.serializers import PlaceListSerializer
from .models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    place = PlaceListSerializer(read_only=True)

    class Meta:
        model  = Favorite
        fields = ["id", "place", "created_at"]
        read_only_fields = ["id", "created_at"]


class FavoriteToggleSerializer(serializers.Serializer):
    """
    POST /favorites/toggle/  { "place_id": "<uuid>" }
    Returns { "status": "added" | "removed" }
    """
    place_id = serializers.UUIDField()