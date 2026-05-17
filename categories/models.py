"""
categories/models.py
====================
Place category taxonomy for the Kokand Tourism Platform.

Intentionally lean — categories are editorial content managed by staff,
not user-generated. The model is i18n-ready via django-modeltranslation
(register title + description without model changes).
"""

from __future__ import annotations

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from common.models import BaseModel


# ---------------------------------------------------------------------------
# Upload paths
# ---------------------------------------------------------------------------

def category_icon_path(instance: "Category", filename: str) -> str:
    return f"categories/{instance.slug}/icon/{filename}"


def category_image_path(instance: "Category", filename: str) -> str:
    return f"categories/{instance.slug}/cover/{filename}"


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

class Category(BaseModel):
    """
    Top-level taxonomy grouping places (e.g. Historical Sites, Restaurants,
    Hotels, Parks, Mosques, Museums).

    SEO fields are stored directly; integrate django-meta for template rendering.
    `is_featured` drives homepage / discovery carousels.
    """

    title = models.CharField(
        max_length=120,
        unique=True,
        db_index=True,
        verbose_name=_("Title"),
    )
    slug = models.SlugField(
        max_length=140,
        unique=True,
        allow_unicode=True,
        verbose_name=_("Slug"),
        help_text=_("Auto-generated from title if left blank."),
    )
    icon = models.ImageField(
        upload_to=category_icon_path,
        blank=True,
        null=True,
        verbose_name=_("Icon"),
        help_text=_("SVG / PNG icon displayed in category chips."),
    )
    image = models.ImageField(
        upload_to=category_image_path,
        blank=True,
        null=True,
        verbose_name=_("Cover image"),
    )
    description = models.TextField(blank=True, verbose_name=_("Description"))
    is_featured = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name=_("Featured"),
        help_text=_("Show in homepage discovery section."),
    )

    # Denormalised for O(1) reads on category cards
    place_count = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Place count"),
    )

    # SEO
    meta_title       = models.CharField(max_length=70,  blank=True, verbose_name=_("Meta title"))
    meta_description = models.CharField(max_length=160, blank=True, verbose_name=_("Meta description"))

    class Meta:
        verbose_name        = _("Category")
        verbose_name_plural = _("Categories")
        ordering            = ["title"]
        indexes = [
            models.Index(fields=["is_featured", "is_active"], name="idx_category_featured_active"),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)