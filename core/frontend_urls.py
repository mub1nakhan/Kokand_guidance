"""
core/frontend_urls.py
=====================
HTML template sahifalari uchun URL marshrutlari.
core/urls.py ichida include qilinadi:
    path("", include("core.frontend_urls"))
"""

from django.urls import path
from django.views.generic import TemplateView


def page(template):
    return TemplateView.as_view(template_name=template)


urlpatterns = [
    path("",                    page("home/index.html"),              name="home"),
    path("places/",             page("places/list.html"),             name="place-list-page"),
    path("places/<slug:slug>/", page("places/detail.html"),           name="place-detail-page"),
    path("routes/",             page("routes/list.html"),             name="route-list-page"),
    path("routes/<slug:slug>/", page("routes/detail.html"),           name="route-detail-page"),
    path("categories/",         page("categories/list.html"),         name="category-list-page"),
    path("map/",                page("map/index.html"),               name="map-page"),
    path("auth/login/",         page("auth/login.html"),              name="login-page"),
    path("auth/register/",      page("auth/register.html"),           name="register-page"),
    path("profile/",            page("users/profile.html"),           name="profile-page"),
    path("profile/edit/",       page("users/profile_edit.html"),      name="profile-edit-page"),
    path("profile/<uuid:id>/",  page("users/public_profile.html"),    name="public-profile-page"),
    path("favorites/",          page("favorites/list.html"),          name="favorites-page"),
    path("about/",              page("static_pages/about.html"),      name="about-page"),
    path("contact/",            page("static_pages/contact.html"),    name="contact-page"),
    path("privacy/",            page("static_pages/privacy.html"),    name="privacy-page"),
]