"""
reviews/views.py
================
Endpoints:
  GET  /places/<slug>/reviews/      — list approved reviews for a place
  POST /places/<slug>/reviews/      — create (authenticated + verified)
  GET  /places/<slug>/reviews/<id>/ — detail
  PUT  /places/<slug>/reviews/<id>/ — update (owner only)
  DEL  /places/<slug>/reviews/<id>/ — delete (owner or admin)
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from common.permissions import IsOwnerOrAdmin, IsVerifiedUser
from places.models import Place
from .models import Review
from .serializers import ReviewDetailSerializer, ReviewListSerializer, ReviewWriteSerializer
from .services import ReviewService


def get_place_or_404(slug: str) -> Place:
    from django.shortcuts import get_object_or_404
    return get_object_or_404(Place, slug=slug, is_active=True)


class ReviewListCreateView(generics.ListCreateAPIView):

    def get_permissions(self):
        if self.request.method == "POST":
            return [permissions.IsAuthenticated(), IsVerifiedUser()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ReviewWriteSerializer
        return ReviewListSerializer

    def get_queryset(self):
        return ReviewService.get_place_reviews(
            place_id=get_place_or_404(self.kwargs["slug"]).pk
        )

    def perform_create(self, serializer):
        place = get_place_or_404(self.kwargs["slug"])
        ReviewService.create_review(
            user=self.request.user,
            place=place,
            rating=serializer.validated_data["rating"],
            comment=serializer.validated_data.get("comment", ""),
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"detail": "Review submitted."}, status=status.HTTP_201_CREATED)


class ReviewRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return [IsOwnerOrAdmin()]
        return [permissions.AllowAny()]

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return ReviewWriteSerializer
        return ReviewDetailSerializer

    def get_queryset(self):
        return Review.objects.filter(
            place__slug=self.kwargs["slug"], is_approved=True
        ).select_related("user", "user__profile").prefetch_related("images")

    def perform_destroy(self, instance):
        ReviewService.delete_review(instance)