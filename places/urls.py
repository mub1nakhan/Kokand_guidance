"""
places/urls.py
==============
Places CRUD + gallery rasmlari + nested reviews.
"""

from django.urls import path, include

from .views import (
    PlaceListCreateView,
    PlaceRetrieveUpdateDestroyView,
    PlaceImageUploadView,
    PlaceImageDestroyView,
)

urlpatterns = [
    # Joylar CRUD
    path("",             PlaceListCreateView.as_view(),            name="place-list"),
    path("<slug:slug>/", PlaceRetrieveUpdateDestroyView.as_view(), name="place-detail"),

    # Gallery rasmlari
    path("<slug:slug>/images/",           PlaceImageUploadView.as_view(),  name="place-image-upload"),
    path("<slug:slug>/images/<uuid:pk>/", PlaceImageDestroyView.as_view(), name="place-image-delete"),

    # Nested reviews — reviews/urls.py dan include qilinadi
    path("<slug:slug>/reviews/", include("reviews.urls")),
]