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
from django.urls import path
from django.views.generic import TemplateView
 
 
# Qisqa yozuv uchun alias
def page(template, name=None):
    """TemplateView shortcut."""
    return TemplateView.as_view(template_name=template)
 
 
urlpatterns = [
 
    # ── Asosiy ────────────────────────────────────────────────────────────
    path(
        "",
        page("home/index.html"),
        name="home",
    ),
 
    # ── Joylar ────────────────────────────────────────────────────────────
    path(
        "places/",
        page("places/list.html"),
        name="place-list-page",
    ),
    path(
        "places/<slug:slug>/",
        page("places/detail.html"),
        name="place-detail-page",
    ),
 
    # ── Marshrutlar ───────────────────────────────────────────────────────
    path(
        "routes/",
        page("routes/list.html"),
        name="route-list-page",
    ),
    path(
        "routes/<slug:slug>/",
        page("routes/detail.html"),
        name="route-detail-page",
    ),
 
    # ── Kategoriyalar ─────────────────────────────────────────────────────
    path(
        "categories/",
        page("categories/list.html"),
        name="category-list-page",
    ),
 
    # ── Xarita ────────────────────────────────────────────────────────────
    path(
        "map/",
        page("map/index.html"),
        name="map-page",
    ),
 
    # ── Auth ──────────────────────────────────────────────────────────────
    path(
        "auth/login/",
        page("auth/login.html"),
        name="login-page",
    ),
    path(
        "auth/register/",
        page("auth/register.html"),
        name="register-page",
    ),
 
    # ── Profil ────────────────────────────────────────────────────────────
    path(
        "profile/",
        page("users/profile.html"),
        name="profile-page",
    ),
    path(
        "profile/edit/",
        page("users/profile_edit.html"),
        name="profile-edit-page",
    ),
    path(
        "profile/<uuid:id>/",
        page("users/public_profile.html"),
        name="public-profile-page",
    ),
 
    # ── Sevimlilar ────────────────────────────────────────────────────────
    path(
        "favorites/",
        page("favorites/list.html"),
        name="favorites-page",
    ),
 
    # ── Statik sahifalar ──────────────────────────────────────────────────
    path(
        "about/",
        page("static_pages/about.html"),
        name="about-page",
    ),
    path(
        "contact/",
        page("static_pages/contact.html"),
        name="contact-page",
    ),
    path(
        "privacy/",
        page("static_pages/privacy.html"),
        name="privacy-page",
    ),
 
]
 