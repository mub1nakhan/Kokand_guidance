"""
categories/serializers.py
=========================
CategoryListSerializer  — lightweight, for dropdowns / chips
CategoryDetailSerializer — full detail with SEO fields
CategoryWriteSerializer  — staff create/update
"""

from rest_framework import serializers

from common.serializers import BaseModelSerializer
from .models import Category


class CategoryListSerializer(BaseModelSerializer):
    """Compact — used in Place serializer and category carousels."""

    class Meta:
        model  = Category
        fields = ["id", "title", "slug", "icon", "image", "is_featured", "place_count"]


class CategoryDetailSerializer(BaseModelSerializer):
    class Meta:
        model  = Category
        fields = [
            "id", "title", "slug", "icon", "image",
            "description", "is_featured", "place_count",
            "meta_title", "meta_description",
            "created_at", "updated_at",
        ]


class CategoryWriteSerializer(BaseModelSerializer):
    """Staff-only create / update — slug auto-generated in model.save()."""

    class Meta:
        model  = Category
        fields = [
            "title", "slug", "icon", "image",
            "description", "is_featured",
            "meta_title", "meta_description",
        ]
        extra_kwargs = {"slug": {"required": False}}