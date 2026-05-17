"""
common/models.py
================
Shared abstract base for the entire Kokand Tourism Platform.
Every app model inherits from BaseModel unless explicitly justified otherwise.
"""

from __future__ import annotations

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class BaseModel(models.Model):
    """
    Platform-wide abstract base model.

    Design decisions:
      - UUID PK: safe for external exposure; no sequential-ID enumeration attacks.
      - auto_now_add / auto_now: set at DB level, immune to application bugs.
      - is_active: soft-delete pattern — never hard-delete content records.
      - created_at carries db_index for time-range filtering on list endpoints.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("ID"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name=_("Created at"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated at"),
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name=_("Active"),
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class ActiveManager(models.Manager):
    """
    Drop-in manager that filters is_active=True by default.
    Attach as `objects` on any concrete model when soft-delete is primary pattern.

    Usage:
        class Place(BaseModel):
            objects = ActiveManager()
            all_objects = models.Manager()   # escape hatch for admin / signals
    """

    def get_queryset(self) -> models.QuerySet:
        return super().get_queryset().filter(is_active=True)