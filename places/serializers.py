"""
places/serializers.py
=====================
Serializer hierarchy (small → large, reuse by nesting):

  PlaceTagSerializer
  PlaceImageSerializer
  PlaceListSerializer      — card view (list endpoints)
  PlaceDetailSerializer    — full detail page
  PlaceWriteSerializer     — create / update (staff / business_owner)
"""

from rest_framework import serializers

from categories.serializers import CategoryListSerializer
from common.serializers import BaseModelSerializer
from users.serializers import UserPublicSerializer
from .models import Place, PlaceImage, PlaceTag


# ---------------------------------------------------------------------------
# Tag
# ---------------------------------------------------------------------------

class PlaceTagSerializer(BaseModelSerializer):
    class Meta:
        model  = PlaceTag
        fields = ["id", "name", "slug"]


# ---------------------------------------------------------------------------
# Gallery image
# ---------------------------------------------------------------------------

class PlaceImageSerializer(BaseModelSerializer):
    class Meta:
        model  = PlaceImage
        fields = ["id", "image", "caption", "order", "is_cover"]
        read_only_fields = ["id"]


# ---------------------------------------------------------------------------
# List (card)
# ---------------------------------------------------------------------------

class PlaceListSerializer(BaseModelSerializer):
    """
    Lightweight — returned on list / search / map endpoints.
    Avoids N+1: category is select_related, tags is prefetch_related.
    """
    category       = CategoryListSerializer(read_only=True)
    tags           = PlaceTagSerializer(many=True, read_only=True)
    price_level_display = serializers.CharField(
        source="get_price_level_display", read_only=True
    )
    is_favorited   = serializers.SerializerMethodField()

    class Meta:
        model  = Place
        fields = [
            "id", "title", "slug", "short_description",
            "main_image", "address", "latitude", "longitude",
            "category", "tags",
            "average_rating", "review_count", "view_count",
            "price_level", "price_level_display",
            "is_featured", "is_favorited",
        ]

    def get_is_favorited(self, obj) -> bool:
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            # Annotated in queryset by FavoritesService.annotate_favorites()
            return getattr(obj, "is_favorited", False)
        return False


# ---------------------------------------------------------------------------
# Detail (full page)
# ---------------------------------------------------------------------------

class PlaceDetailSerializer(BaseModelSerializer):
    category   = CategoryListSerializer(read_only=True)
    tags       = PlaceTagSerializer(many=True, read_only=True)
    images     = PlaceImageSerializer(many=True, read_only=True)
    created_by = UserPublicSerializer(read_only=True)
    price_level_display = serializers.CharField(
        source="get_price_level_display", read_only=True
    )
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model  = Place
        fields = [
            "id", "title", "slug",
            "short_description", "description",
            "address", "latitude", "longitude",
            "main_image", "images",
            "category", "tags",
            "phone", "website", "working_hours",
            "price_level", "price_level_display", "average_price",
            "average_rating", "review_count", "view_count",
            "is_featured", "is_favorited",
            "meta_title", "meta_description", "meta_keywords",
            "created_by", "created_at", "updated_at",
        ]

    def get_is_favorited(self, obj) -> bool:
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return getattr(obj, "is_favorited", False)
        return False


# ---------------------------------------------------------------------------
# Write (create / update)
# ---------------------------------------------------------------------------

class PlaceWriteSerializer(BaseModelSerializer):
    """
    Used for POST / PUT / PATCH by staff and business_owners.
    Slug is auto-generated in model.save() if omitted.
    tag_ids accepts a list of PlaceTag UUIDs.
    """
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=PlaceTag.objects.all(),
        many=True,
        source="tags",
        required=False,
        write_only=True,
    )

    class Meta:
        model  = Place
        fields = [
            "category", "title", "slug",
            "short_description", "description",
            "address", "latitude", "longitude",
            "main_image",
            "phone", "website", "working_hours",
            "price_level", "average_price",
            "is_featured",
            "meta_title", "meta_description", "meta_keywords",
            "tag_ids",
        ]
        extra_kwargs = {"slug": {"required": False}}

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        place = Place.objects.create(**validated_data)
        place.tags.set(tags)
        return place

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance


# ---------------------------------------------------------------------------
# PlaceImage upload
# ---------------------------------------------------------------------------

class PlaceImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PlaceImage
        fields = ["image", "caption", "order", "is_cover"]

    def create(self, validated_data):
        place = self.context["place"]
        return PlaceImage.objects.create(place=place, **validated_data)