"""
places/models.py
================
Core content layer for the Kokand Tourism Platform.

Models:
  Place       — primary point-of-interest entity
  PlaceImage  — ordered gallery images for a Place
  PlaceTag    — folksonomy tags (many-to-many with Place)

Design decisions:
  - Denormalised average_rating / view_count for O(1) list API reads.
    Recompute average_rating via post_save / post_delete signal on Review.
    Increment view_count with F() expression — no race conditions.
  - working_hours as JSONField: flexible for irregular schedules, holiday
    overrides, and future structured-hours UI without schema migrations.
  - Geo fields as DecimalField (not PointField) to avoid PostGIS dependency;
    swap to PointField + spatial index if PostGIS is introduced later.
  - PlaceTag uses a clean M2M through Place.tags so tag API stays thin.
"""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from categories.models import Category
from common.models import ActiveManager, BaseModel


# ---------------------------------------------------------------------------
# Upload paths
# ---------------------------------------------------------------------------

def place_main_image_path(instance: "Place", filename: str) -> str:
    return f"places/{instance.slug}/main/{filename}"


def place_gallery_path(instance: "PlaceImage", filename: str) -> str:
    return f"places/{instance.place.slug}/gallery/{filename}"


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

phone_validator = RegexValidator(
    regex=r"^\+?[1-9]\d{6,14}$",
    message=_("Enter a valid international phone number (e.g. +998901234567)."),
)

lat_validators = [MinValueValidator(Decimal("-90")), MaxValueValidator(Decimal("90"))]
lng_validators = [MinValueValidator(Decimal("-180")), MaxValueValidator(Decimal("180"))]


# ---------------------------------------------------------------------------
# Choices
# ---------------------------------------------------------------------------

class PriceLevel(models.IntegerChoices):
    FREE     = 0, _("Free")
    BUDGET   = 1, _("Budget  ₩")
    MODERATE = 2, _("Moderate ₩₩")
    UPSCALE  = 3, _("Upscale ₩₩₩")
    LUXURY   = 4, _("Luxury ₩₩₩₩")


# ---------------------------------------------------------------------------
# PlaceTag
# ---------------------------------------------------------------------------

class PlaceTag(BaseModel):
    """
    Lightweight folksonomy tag.
    Staff-curated or user-suggested (moderated via is_active).
    """

    name = models.CharField(max_length=60, unique=True, db_index=True, verbose_name=_("Name"))
    slug = models.SlugField(max_length=80, unique=True, allow_unicode=True, verbose_name=_("Slug"))

    class Meta:
        verbose_name        = _("Place tag")
        verbose_name_plural = _("Place tags")
        ordering            = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Place
# ---------------------------------------------------------------------------

class Place(BaseModel):
    """
    Primary point-of-interest record.

    Indexes are designed around the most frequent API query patterns:
      - List by category + active
      - Featured carousel
      - Geo bounding-box (lat/lng)
      - Rating sort
      - Full-text search via Postgres (add GinIndex on tsvector when needed)
    """

    # --- Relations ---
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="places",
        db_index=True,
        verbose_name=_("Category"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_places",
        db_index=True,
        verbose_name=_("Created by"),
    )
    tags = models.ManyToManyField(
        PlaceTag,
        blank=True,
        related_name="places",
        verbose_name=_("Tags"),
    )

    # --- Identity ---
    title = models.CharField(max_length=255, db_index=True, verbose_name=_("Title"))
    slug  = models.SlugField(
        max_length=280,
        unique=True,
        allow_unicode=True,
        verbose_name=_("Slug"),
    )

    # --- Content ---
    short_description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("Short description"),
        help_text=_("Used in list cards (max 500 chars)."),
    )
    description = models.TextField(blank=True, verbose_name=_("Full description"))

    # --- Location ---
    address   = models.CharField(max_length=500, blank=True, verbose_name=_("Address"))
    latitude  = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True,
        validators=lat_validators,
        verbose_name=_("Latitude"),
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        null=True, blank=True,
        validators=lng_validators,
        verbose_name=_("Longitude"),
    )

    # --- Media ---
    main_image = models.ImageField(
        upload_to=place_main_image_path,
        blank=True, null=True,
        verbose_name=_("Main image"),
    )

    # --- Contact ---
    phone   = models.CharField(max_length=20, blank=True, validators=[phone_validator], verbose_name=_("Phone"))
    website = models.URLField(max_length=255, blank=True, verbose_name=_("Website"))

    # --- Operations ---
    working_hours = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Working hours"),
        help_text=_('e.g. {"mon":"09:00-18:00","fri":"09:00-17:00","sun":"closed"}'),
    )
    price_level = models.PositiveSmallIntegerField(
        choices=PriceLevel.choices,
        default=PriceLevel.FREE,
        db_index=True,
        verbose_name=_("Price level"),
    )
    average_price = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        validators=[MinValueValidator(Decimal("0"))],
        verbose_name=_("Average price (UZS)"),
    )

    # --- Discovery ---
    is_featured    = models.BooleanField(default=False, db_index=True, verbose_name=_("Featured"))
    view_count     = models.PositiveIntegerField(default=0, verbose_name=_("View count"))
    average_rating = models.DecimalField(
        max_digits=3, decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("5"))],
        verbose_name=_("Average rating"),
    )
    review_count = models.PositiveIntegerField(default=0, verbose_name=_("Review count"))

    # --- SEO ---
    meta_title       = models.CharField(max_length=70,  blank=True, verbose_name=_("Meta title"))
    meta_description = models.CharField(max_length=160, blank=True, verbose_name=_("Meta description"))
    meta_keywords    = models.CharField(max_length=255, blank=True, verbose_name=_("Meta keywords"))

    # Managers
    objects     = ActiveManager()
    all_objects = models.Manager()

    class Meta:
        verbose_name        = _("Place")
        verbose_name_plural = _("Places")
        ordering            = ["-is_featured", "-created_at"]
        indexes = [
            models.Index(fields=["category", "is_active"],    name="idx_place_category_active"),
            models.Index(fields=["is_featured", "is_active"], name="idx_place_featured_active"),
            models.Index(fields=["latitude", "longitude"],    name="idx_place_geo"),
            models.Index(fields=["-average_rating"],          name="idx_place_rating_desc"),
            models.Index(fields=["-view_count"],              name="idx_place_views_desc"),
            models.Index(fields=["price_level", "is_active"], name="idx_place_price_active"),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# PlaceImage
# ---------------------------------------------------------------------------

class PlaceImage(BaseModel):
    """
    Ordered gallery image for a Place.
    Lower `order` value = displayed first in the carousel.
    Unique constraint prevents duplicate ordinal slots per place.
    """

    place   = models.ForeignKey(Place, on_delete=models.CASCADE, related_name="images", db_index=True, verbose_name=_("Place"))
    image   = models.ImageField(upload_to=place_gallery_path, verbose_name=_("Image"))
    caption = models.CharField(max_length=255, blank=True, verbose_name=_("Caption"))
    order   = models.PositiveSmallIntegerField(default=0, db_index=True, verbose_name=_("Display order"))
    is_cover = models.BooleanField(
        default=False,
        verbose_name=_("Use as cover"),
        help_text=_("Replaces main_image in API responses when set."),
    )

    class Meta:
        verbose_name        = _("Place image")
        verbose_name_plural = _("Place images")
        ordering            = ["place", "order"]
        constraints = [
            models.UniqueConstraint(fields=["place", "order"], name="unique_place_image_order"),
        ]

    def __str__(self) -> str:
        return f"{self.place.title} — image #{self.order}"