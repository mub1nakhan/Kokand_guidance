"""
common/serializers.py
=====================
Shared serializer base and mixins reused across all apps.
"""

from rest_framework import serializers


class BaseModelSerializer(serializers.ModelSerializer):
    """
    Read-only UUID + timestamp fields injected into every serializer
    that inherits from this base. Concrete serializers declare their
    own `fields` — this just guarantees the audit columns are always present.
    """

    id         = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class WritableSerializerMixin:
    """
    Mixin that separates read (nested) from write (PK) representations.

    Usage:
        class PlaceSerializer(WritableSerializerMixin, BaseModelSerializer):
            category = CategorySerializer(read_only=True)
            category_id = serializers.PrimaryKeyRelatedField(
                queryset=Category.objects.all(), source="category", write_only=True
            )
    """
    pass