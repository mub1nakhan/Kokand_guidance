"""
reviews/urls.py
===============
Reviews endpointlari places app ichida nested holda ishlatiladi.
places/urls.py orqali quyidagi yo'llar bilan ulanadi:
  /api/v1/places/<slug>/reviews/
  /api/v1/places/<slug>/reviews/<pk>/
"""

from django.urls import path

from .views import (
    ReviewListCreateView,
    ReviewRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("", ReviewListCreateView.as_view(), name="place-review-list"),
    path("<int:pk>/", ReviewRetrieveUpdateDestroyView.as_view(), name="place-review-detail"),
]