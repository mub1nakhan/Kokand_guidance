from django.urls import path
 
from .views import (
    TourRouteListCreateView,
    TourRouteRetrieveUpdateDestroyView,
)
 
urlpatterns = [
    path("",            TourRouteListCreateView.as_view(),            name="route-list"),
    path("<slug:slug>/", TourRouteRetrieveUpdateDestroyView.as_view(), name="route-detail"),
]
 