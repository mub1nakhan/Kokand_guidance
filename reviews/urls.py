"""
reviews/urls.py
===============
Reviews endpointlari places app ichida nested holda ishlatiladi.
places/urls.py orqali quyidagi yo'llar bilan ulanadi:
  GET/POST  /api/v1/places/<slug>/reviews/
  GET/PUT/DEL /api/v1/places/<slug>/reviews/<pk>/
  POST      /api/v1/places/<slug>/reviews/<pk>/images/      (yangi)
  DELETE    /api/v1/places/<slug>/reviews/<pk>/images/<img_pk>/ (yangi)
  POST      /api/v1/places/<slug>/reviews/<pk>/flag/        (yangi)
"""

from django.urls import path

from .views import (
    ReviewListCreateView,
    ReviewRetrieveUpdateDestroyView,
    ReviewImageUploadView,
    ReviewImageDestroyView,
    ReviewFlagView,
)

urlpatterns = [
    path("", ReviewListCreateView.as_view(), name="place-review-list"),
    path("<int:pk>/", ReviewRetrieveUpdateDestroyView.as_view(), name="place-review-detail"),
    path("<int:pk>/images/", ReviewImageUploadView.as_view(), name="review-image-upload"),
    path("<int:pk>/images/<int:img_pk>/", ReviewImageDestroyView.as_view(), name="review-image-delete"),
    path("<int:pk>/flag/", ReviewFlagView.as_view(), name="review-flag"),
]

