"""
places/views.py
===============
Endpoints:
  GET  /places/                    — list + filter + search
  POST /places/                    — create (staff / business_owner)
  GET  /places/<slug>/             — detail (increments view_count)
  PUT  /places/<slug>/             — update (owner / staff)
  DEL  /places/<slug>/             — soft-delete (owner / staff)
  POST /places/<slug>/images/      — upload gallery image
  DEL  /places/<slug>/images/<id>/ — delete gallery image
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsOwnerOrAdmin, IsStaffOrBusinessOwner
from .models import Place, PlaceImage
from .serializers import (
    PlaceDetailSerializer,
    PlaceImageUploadSerializer,
    PlaceListSerializer,
    PlaceWriteSerializer,
)
from .services import PlaceService


class PlaceListCreateView(generics.ListCreateAPIView):
    """
    GET  — public list with filtering, search, ordering
    POST — staff / business_owner only
    """
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["category__slug", "price_level", "is_featured"]
    search_fields    = ["title", "short_description", "address", "tags__name"]
    ordering_fields  = ["average_rating", "view_count", "created_at", "title"]
    ordering         = ["-is_featured", "-created_at"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsStaffOrBusinessOwner()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PlaceWriteSerializer
        return PlaceListSerializer

    def get_queryset(self):
        return PlaceService.get_list_queryset(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PlaceRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET  — public detail, increments view_count
    PUT  — owner or staff
    DEL  — soft-delete, owner or staff
    """
    lookup_field = "slug"

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return [IsOwnerOrAdmin()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return PlaceWriteSerializer
        return PlaceDetailSerializer

    def get_queryset(self):
        return PlaceService.get_detail_queryset(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        PlaceService.increment_view_count(instance.pk)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save(update_fields=["is_active"])


class PlaceImageUploadView(generics.CreateAPIView):
    """POST /places/<slug>/images/ — upload a gallery image"""
    serializer_class = PlaceImageUploadSerializer
    parser_classes   = [MultiPartParser, FormParser]
    permission_classes = [IsStaffOrBusinessOwner]

    def get_place(self):
        return Place.objects.get(slug=self.kwargs["slug"], is_active=True)

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["place"] = self.get_place()
        return ctx


class PlaceImageDestroyView(generics.DestroyAPIView):
    """DELETE /places/<slug>/images/<id>/"""
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        return PlaceImage.objects.filter(place__slug=self.kwargs["slug"])

    def get_object(self):
        return self.get_queryset().get(pk=self.kwargs["pk"])