from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# --- Users ---
from users.views import (
    RegisterView,
    ChangePasswordView,
    CurrentUserView,
    UserPublicDetailView,
)

# --- Categories ---
from categories.views import (
    CategoryListCreateView,
    CategoryRetrieveUpdateDestroyView,
)

# --- Places ---
from places.views import (
    PlaceListCreateView,
    PlaceRetrieveUpdateDestroyView,
    PlaceImageUploadView,
    PlaceImageDestroyView,
)

# --- Reviews ---
from reviews.views import (
    ReviewListCreateView,
    ReviewRetrieveUpdateDestroyView,
)

# --- Routes ---
from routes.views import (
    TourRouteListCreateView,
    TourRouteRetrieveUpdateDestroyView,
)

# --- Favorites ---
from favorites.views import (
    FavoriteListView,
    FavoriteToggleView,
)


urlpatterns = [

    # ------------------------------------------------------------------ Admin
    path("admin/", admin.site.urls),

    # ------------------------------------------------------------------ Auth
    path("api/v1/auth/register/",        RegisterView.as_view(),        name="auth-register"),
    path("api/v1/auth/login/",           TokenObtainPairView.as_view(), name="auth-login"),
    path("api/v1/auth/token/refresh/",   TokenRefreshView.as_view(),    name="auth-token-refresh"),
    path("api/v1/auth/change-password/", ChangePasswordView.as_view(),  name="auth-change-password"),

    # ------------------------------------------------------------------ Users
    path("api/v1/users/me/",        CurrentUserView.as_view(),      name="user-me"),
    path("api/v1/users/<uuid:id>/", UserPublicDetailView.as_view(), name="user-detail"),

    # ------------------------------------------------------------------ Categories
    path("api/v1/categories/",            CategoryListCreateView.as_view(),           name="category-list"),
    path("api/v1/categories/<slug:slug>/", CategoryRetrieveUpdateDestroyView.as_view(), name="category-detail"),

    # ------------------------------------------------------------------ Places
    path("api/v1/places/",            PlaceListCreateView.as_view(),           name="place-list"),
    path("api/v1/places/<slug:slug>/", PlaceRetrieveUpdateDestroyView.as_view(), name="place-detail"),

    # Place gallery images
    path("api/v1/places/<slug:slug>/images/",          PlaceImageUploadView.as_view(),  name="place-image-upload"),
    path("api/v1/places/<slug:slug>/images/<uuid:pk>/", PlaceImageDestroyView.as_view(), name="place-image-delete"),

    # ------------------------------------------------------------------ Reviews (nested under place)
    path("api/v1/places/<slug:slug>/reviews/",          ReviewListCreateView.as_view(),           name="place-review-list"),
    path("api/v1/places/<slug:slug>/reviews/<int:pk>/", ReviewRetrieveUpdateDestroyView.as_view(), name="place-review-detail"),

    # ------------------------------------------------------------------ Routes
    path("api/v1/routes/",            TourRouteListCreateView.as_view(),           name="route-list"),
    path("api/v1/routes/<slug:slug>/", TourRouteRetrieveUpdateDestroyView.as_view(), name="route-detail"),

    # ------------------------------------------------------------------ Favorites
    path("api/v1/favorites/",         FavoriteListView.as_view(),   name="favorite-list"),
    path("api/v1/favorites/toggle/",  FavoriteToggleView.as_view(), name="favorite-toggle"),

]

# Media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
