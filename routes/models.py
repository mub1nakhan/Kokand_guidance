"""
routes/models.py
================
Curated tour route layer for the Kokand Tourism Platform.

Models:
  TourRoute   — a named, themed sequence of places forming a walking / driving tour.
  RoutePlace  — explicit M2M through-model tracking stop order, duration, and notes.

Design decisions:
  - Explicit through-model (RoutePlace) instead of bare ManyToManyField:
    stop ordering, per-stop duration estimates, and guide notes are first-class
    data — not afterthoughts. Adding this later would require a data migration.
  - map_data as JSONField: stores GeoJSON LineString or encoded polyline for
    the route path without requiring PostGIS. Swap to GeometryField if PostGIS
    is introduced.
  - distance stored as PositiveIntegerField (metres) for cheap sorting / filtering
    without unit-conversion logic in the application layer.
  - Two UniqueConstraints on RoutePlace guard both M2M integrity and ordinal
    uniqueness at the DB level.
"""

from __future__ import annotations

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from common.models import BaseModel, ActiveManager
from places.models import Place


# ---------------------------------------------------------------------------
# Upload path
# ---------------------------------------------------------------------------

def route_cover_path(instance: "TourRoute", filename: str) -> str:
    return f"routes/{instance.slug}/cover/{filename}"


# ---------------------------------------------------------------------------
# Choices
# ---------------------------------------------------------------------------

class TransportMode(models.TextChoices):
    WALKING  = "walking",  _("Walking")
    CYCLING  = "cycling",  _("Cycling")
    DRIVING  = "driving",  _("Driving")
    TRANSIT  = "transit",  _("Public transit")
    MIXED    = "mixed",    _("Mixed")


class DifficultyLevel(models.TextChoices):
    EASY     = "easy",     _("Easy")
    MODERATE = "moderate", _("Moderate")
    HARD     = "hard",     _("Hard")


# ---------------------------------------------------------------------------
# TourRoute
# ---------------------------------------------------------------------------

class TourRoute(BaseModel):
    """
    A curated multi-stop tour through Kokand.

    estimated_duration — total time in minutes (walk + exploration).
    distance           — total path length in metres.
    map_data           — GeoJSON / encoded polyline for the route overlay.
    """

    title = models.CharField(max_length=255, db_index=True, verbose_name=_("Title"))
    slug  = models.SlugField(
        max_length=280,
        unique=True,
        allow_unicode=True,
        verbose_name=_("Slug"),
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))
    cover_image = models.ImageField(
        upload_to=route_cover_path,
        blank=True,
        null=True,
        verbose_name=_("Cover image"),
    )

    # Route metadata
    transport_mode     = models.CharField(
        max_length=10,
        choices=TransportMode.choices,
        default=TransportMode.WALKING,
        db_index=True,
        verbose_name=_("Transport mode"),
    )
    difficulty         = models.CharField(
        max_length=10,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.EASY,
        db_index=True,
        verbose_name=_("Difficulty"),
    )
    estimated_duration = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Estimated duration (min)"),
        help_text=_("Total time including stops, in minutes."),
    )
    distance = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Distance (metres)"),
    )
    map_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Map data"),
        help_text=_("GeoJSON LineString or Google encoded polyline for the route path."),
    )

    # Discovery
    is_featured  = models.BooleanField(default=False, db_index=True, verbose_name=_("Featured"))
    view_count   = models.PositiveIntegerField(default=0, verbose_name=_("View count"))

    # Explicit M2M via through-model
    places = models.ManyToManyField(
        Place,
        through="RoutePlace",
        related_name="tour_routes",
        verbose_name=_("Places"),
    )

    # SEO
    meta_title       = models.CharField(max_length=70,  blank=True, verbose_name=_("Meta title"))
    meta_description = models.CharField(max_length=160, blank=True, verbose_name=_("Meta description"))


    # Managers
    objects     = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name        = _("Tour route")
        verbose_name_plural = _("Tour routes")
        ordering            = ["-is_featured", "-created_at"]
        indexes = [
            models.Index(fields=["is_featured", "is_active"],  name="idx_route_featured_active"),
            models.Index(fields=["transport_mode", "is_active"], name="idx_route_mode_active"),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    @property
    def stop_count(self) -> int:
        """Fast count via annotated queryset in the view layer; fallback here."""
        return self.route_places.count()


# ---------------------------------------------------------------------------
# RoutePlace (through-model)
# ---------------------------------------------------------------------------

class RoutePlace(models.Model):
    """
    Explicit through-model for TourRoute ↔ Place.

    Stores:
      order             — display / navigation sequence (1-based).
      duration_at_stop  — suggested time to spend at this stop (minutes).
      transport_to_next — how to travel from this stop to the next.
      notes             — guide tip shown in the stop detail card.

    Constraints:
      unique_route_place      — a place cannot appear twice in the same route.
      unique_route_stop_order — no two stops share the same ordinal in a route.
    """

    id = models.BigAutoField(primary_key=True)

    tour_route = models.ForeignKey(
        TourRoute,
        on_delete=models.CASCADE,
        related_name="route_places",
        db_index=True,
        verbose_name=_("Tour route"),
    )
    place = models.ForeignKey(
        Place,
        on_delete=models.CASCADE,
        related_name="route_entries",
        db_index=True,
        verbose_name=_("Place"),
    )

    order = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_("Stop order"),
        help_text=_("1-based position in the route sequence."),
    )
    duration_at_stop = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Duration at stop (min)"),
    )
    transport_to_next = models.CharField(
        max_length=10,
        choices=TransportMode.choices,
        blank=True,
        verbose_name=_("Transport to next stop"),
    )
    notes = models.CharField(max_length=500, blank=True, verbose_name=_("Guide notes"))

    class Meta:
        verbose_name        = _("Route stop")
        verbose_name_plural = _("Route stops")
        ordering            = ["tour_route", "order"]
        constraints = [
            models.UniqueConstraint(
                fields=["tour_route", "place"],
                name="unique_route_place",
            ),
            models.UniqueConstraint(
                fields=["tour_route", "order"],
                name="unique_route_stop_order",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.tour_route.title} — stop {self.order}: {self.place.title}"