"""
categories/views.py
===================
GET  /categories/         — list (public)
POST /categories/         — create (admin/staff)
GET  /categories/<slug>/  — detail (public)
PUT  /categories/<slug>/  — update (admin/staff)
DEL  /categories/<slug>/  — delete (admin/staff)
"""

from rest_framework import generics, permissions

from common.permissions import IsAdminOrReadOnly
from .models import Category
from .services import CategoryService
from .serializers import (
    CategoryDetailSerializer,
    CategoryListSerializer,
    CategoryWriteSerializer,
)


class CategoryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return CategoryService.get_list_queryset()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CategoryWriteSerializer
        return CategoryListSerializer


class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"

    def get_queryset(self):
        return CategoryService.get_list_queryset()

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return CategoryWriteSerializer
        return CategoryDetailSerializer

    def perform_destroy(self, instance):
        # Soft-delete
        instance.is_active = False
        instance.save(update_fields=["is_active"])