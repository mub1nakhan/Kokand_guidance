from django.urls import path
 
from .views import (
    PlaceListCreateView,
    PlaceRetrieveUpdateDestroyView,
    PlaceImageUploadView,
    PlaceImageDestroyView,
)
from reviews.views import (
    ReviewListCreateView,
    ReviewRetrieveUpdateDestroyView,
)
 
urlpatterns = [
    # Joylar CRUD
    path("",            PlaceListCreateView.as_view(),            name="place-list"),
    path("<slug:slug>/", PlaceRetrieveUpdateDestroyView.as_view(), name="place-detail"),
 
    # Gallery rasmlari
    path("<slug:slug>/images/",           PlaceImageUploadView.as_view(),  name="place-image-upload"),
    path("<slug:slug>/images/<uuid:pk>/", PlaceImageDestroyView.as_view(), name="place-image-delete"),
 
    # Nested reviews
    path("<slug:slug>/reviews/",          ReviewListCreateView.as_view(),           name="place-review-list"),
    path("<slug:slug>/reviews/<int:pk>/", ReviewRetrieveUpdateDestroyView.as_view(), name="place-review-detail"),
]
 