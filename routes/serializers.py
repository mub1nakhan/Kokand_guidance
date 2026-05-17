"""
routes/serializers.py
=====================
RoutePlaceSerializer      — stop detail embedded inside a route
TourRouteListSerializer   — card view
TourRouteDetailSerializer — full detail with ordered stops
TourRouteWriteSerializer  — staff create / update with stop management
"""

from rest_framework import serializers

from common.serializers import BaseModelSerializer
from places.serializers import PlaceListSerializer
from .models import RoutePlace, TourRoute


# ---------------------------------------------------------------------------
# Route stop (through-model)
# ---------------------------------------------------------------------------

class RoutePlaceSerializer(serializers.ModelSerializer):
    place = PlaceListSerializer(read_only=True)

    class Meta:
        model  = RoutePlace
        fields = [
            "id", "order", "place",
            "duration_at_stop", "transport_to_next", "notes",
        ]


class RoutePlaceWriteSerializer(serializers.ModelSerializer):
    """Used when updating stops on an existing route."""

    class Meta:
        model  = RoutePlace
        fields = ["place", "order", "duration_at_stop", "transport_to_next", "notes"]


# ---------------------------------------------------------------------------
# List (card)
# ---------------------------------------------------------------------------

class TourRouteListSerializer(BaseModelSerializer):
    transport_mode_display = serializers.CharField(
        source="get_transport_mode_display", read_only=True
    )
    difficulty_display = serializers.CharField(
        source="get_difficulty_display", read_only=True
    )
    stop_count = serializers.IntegerField(read_only=True)   # annotated in service

    class Meta:
        model  = TourRoute
        fields = [
            "id", "title", "slug", "cover_image",
            "estimated_duration", "distance",
            "transport_mode", "transport_mode_display",
            "difficulty", "difficulty_display",
            "is_featured", "stop_count",
        ]


# ---------------------------------------------------------------------------
# Detail
# ---------------------------------------------------------------------------

class TourRouteDetailSerializer(BaseModelSerializer):
    stops = RoutePlaceSerializer(source="route_places", many=True, read_only=True)
    transport_mode_display = serializers.CharField(
        source="get_transport_mode_display", read_only=True
    )
    difficulty_display = serializers.CharField(
        source="get_difficulty_display", read_only=True
    )

    class Meta:
        model  = TourRoute
        fields = [
            "id", "title", "slug", "description", "cover_image",
            "estimated_duration", "distance",
            "transport_mode", "transport_mode_display",
            "difficulty", "difficulty_display",
            "map_data", "is_featured", "view_count",
            "stops",
            "meta_title", "meta_description",
            "created_at", "updated_at",
        ]


# ---------------------------------------------------------------------------
# Write
# ---------------------------------------------------------------------------

class TourRouteWriteSerializer(BaseModelSerializer):
    """
    Staff create / update.
    stops_data is handled separately via the nested write pattern in the service.
    """
    stops_data = RoutePlaceWriteSerializer(many=True, required=False, write_only=True)

    class Meta:
        model  = TourRoute
        fields = [
            "title", "slug", "description", "cover_image",
            "estimated_duration", "distance",
            "transport_mode", "difficulty",
            "map_data", "is_featured",
            "meta_title", "meta_description",
            "stops_data",
        ]
        extra_kwargs = {"slug": {"required": False}}

    def create(self, validated_data):
        stops_data = validated_data.pop("stops_data", [])
        route = TourRoute.objects.create(**validated_data)
        self._sync_stops(route, stops_data)
        return route

    def update(self, instance, validated_data):
        stops_data = validated_data.pop("stops_data", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if stops_data is not None:
            self._sync_stops(instance, stops_data)
        return instance

    @staticmethod
    def _sync_stops(route: TourRoute, stops_data: list) -> None:
        """Replace all stops atomically."""
        route.route_places.all().delete()
        RoutePlace.objects.bulk_create([
            RoutePlace(tour_route=route, **stop)
            for stop in stops_data
        ])