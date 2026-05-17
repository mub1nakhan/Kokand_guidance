"""
routes/views.py
===============
Endpoints:
  GET  /routes/         — list (public)
  POST /routes/         — create (staff)
  GET  /routes/<slug>/  — detail (increments view_count)
  PUT  /routes/<slug>/  — update (staff)
  DEL  /routes/<slug>/  — soft-delete (staff)
"""

from rest_framework import generics, permissions

from common.permissions import IsAdminOrReadOnly
from .models import TourRoute
from .serializers import (
    TourRouteDetailSerializer,
    TourRouteListSerializer,
    TourRouteWriteSerializer,
)
from .services import TourRouteService


class TourRouteListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TourRouteWriteSerializer
        return TourRouteListSerializer

    def get_queryset(self):
        return TourRouteService.get_list_queryset()


class TourRouteRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return TourRouteWriteSerializer
        return TourRouteDetailSerializer

    def get_queryset(self):
        return TourRouteService.get_detail_queryset()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        TourRouteService.increment_view_count(instance.pk)
        return super().retrieve(request, *args, **kwargs)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active"])