"""
core/urls.py
============
Markaziy URL konfiguratsiyasi.
Har bir app o'zining urls.py ga ega — bu yerda faqat include() qilinadi.

Endpointlar xaritasi:
  /admin/                  — Django admin
  /api/schema/             — OpenAPI schema (JSON)
  /api/docs/               — Swagger UI
  /api/docs/redoc/         — ReDoc UI
  /api/v1/auth/...         — Register, Login, Refresh, Change-password
  /api/v1/users/...        — Me, Public profile
  /api/v1/categories/...   — Category CRUD
  /api/v1/places/...       — Place CRUD + images + nested reviews
  /api/v1/routes/...       — TourRoute CRUD
  /api/v1/favorites/...    — List + Toggle
  /media/...               — Uploaded files (DEBUG only)
  /static/...              — Static files (DEBUG only)
"""

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from users.urls import auth_urlpatterns
from django.views.generic import TemplateView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

urlpatterns = [

    # ── Admin ──────────────────────────────────────────────────────────────
    path("admin/", admin.site.urls),

    # ── API Docs (Swagger / ReDoc) ─────────────────────────────────────────
    path("api/schema/",     SpectacularAPIView.as_view(),                      name="schema"),
    path("api/docs/",       SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"),   name="redoc"),

    # ── Auth ───────────────────────────────────────────────────────────────
    path("api/v1/auth/", include((auth_urlpatterns, "auth"))),

    # ── Users ──────────────────────────────────────────────────────────────
    path("api/v1/users/", include("users.urls")),

    # ── Categories ─────────────────────────────────────────────────────────
    path("api/v1/categories/", include("categories.urls")),

    # ── Places  (reviews nested places/urls.py ichida) ────────────────────
    path("api/v1/places/", include("places.urls")),

    # ── Routes ─────────────────────────────────────────────────────────────
    path("api/v1/routes/", include("routes.urls")),

    # ── Favorites ──────────────────────────────────────────────────────────
    path("api/v1/favorites/", include("favorites.urls")),

]

# ── Frontend template sahifalari ────────────────────────────────────────────
urlpatterns += [
    path("", include("core.frontend_urls")),
]

# ── Media & Static — faqat development rejimida ────────────────────────────
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)