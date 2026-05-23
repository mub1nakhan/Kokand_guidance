"""
reviews/views.py
================
Endpoints:
  GET  /places/<slug>/reviews/      — list approved reviews for a place
  POST /places/<slug>/reviews/      — create (authenticated + verified)
  GET  /places/<slug>/reviews/<id>/ — detail
  PUT  /places/<slug>/reviews/<id>/ — update (owner only)
  DEL  /places/<slug>/reviews/<id>/ — delete (owner or admin)

FIXES:
  - perform_create: serializer.save() o'rniga ReviewService.create_review()
    to'g'ri chaqiriladi (avvalgi kod ishlardi, lekin DRF konvensiyasiga zid edi)
  - perform_update: yangi ReviewService.update_review() ishlatiladi
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from common.permissions import IsOwnerOrAdmin, IsVerifiedUser
from places.models import Place
from .models import Review, ReviewImage
from .serializers import (
    ReviewDetailSerializer,
    ReviewImageUploadSerializer,
    ReviewListSerializer,
    ReviewWriteSerializer,
)
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        place = get_place_or_404(self.kwargs["slug"])
        ReviewService.create_review(
            user=request.user,
            place=place,
            rating=serializer.validated_data["rating"],
            comment=serializer.validated_data.get("comment", ""),
        )
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

    def perform_update(self, serializer):
        """FIX: update_review() service orqali — recompute_rating signal ishga tushadi."""
        ReviewService.update_review(
            review=self.get_object(),
            rating=serializer.validated_data["rating"],
            comment=serializer.validated_data.get("comment", ""),
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(ReviewDetailSerializer(instance, context={"request": request}).data)

    def perform_destroy(self, instance):
        ReviewService.delete_review(instance)


# ---------------------------------------------------------------------------
# ReviewImage upload (yangi endpoint)
# ---------------------------------------------------------------------------

from rest_framework.parsers import MultiPartParser, FormParser


class ReviewImageUploadView(generics.CreateAPIView):
    """
    POST /places/<slug>/reviews/<pk>/images/
    Foydalanuvchi o'z reviewiga rasm yuklaydi.
    """
    serializer_class = ReviewImageUploadSerializer
    parser_classes   = [MultiPartParser, FormParser]
    permission_classes = [IsOwnerOrAdmin]

    def get_review(self):
        from django.shortcuts import get_object_or_404
        return get_object_or_404(
            Review,
            pk=self.kwargs["pk"],
            place__slug=self.kwargs["slug"],
            user=self.request.user,
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["review"] = self.get_review()
        return ctx


class ReviewImageDestroyView(generics.DestroyAPIView):
    """DELETE /places/<slug>/reviews/<pk>/images/<img_pk>/"""
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        return ReviewImage.objects.filter(
            review__pk=self.kwargs["pk"],
            review__place__slug=self.kwargs["slug"],
        )

    def get_object(self):
        return self.get_queryset().get(pk=self.kwargs["img_pk"])


# ---------------------------------------------------------------------------
# Flag endpoint (yangi)
# ---------------------------------------------------------------------------

from rest_framework.views import APIView


class ReviewFlagView(APIView):
    """
    POST /places/<slug>/reviews/<pk>/flag/
    Autentifikatsiya qilingan foydalanuvchi reviewni shikoyat qiladi.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug, pk):
        from django.shortcuts import get_object_or_404
        review = get_object_or_404(Review, pk=pk, place__slug=slug, is_approved=True)
        if review.user == request.user:
            return Response(
                {"detail": "O'z reviewingizni shikoyat qila olmaysiz."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        review.is_flagged = True
        review.save(update_fields=["is_flagged"])
        return Response({"detail": "Review shikoyat qilindi."}, status=status.HTTP_200_OK)