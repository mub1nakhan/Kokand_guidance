"""
routes/services.py
==================
"""

from django.db.models import Count, F, QuerySet


class TourRouteService:

    @staticmethod
    def get_list_queryset() -> QuerySet:
        from .models import TourRoute
        return (
            TourRoute.objects
            .filter(is_active=True)
            .annotate(stop_count=Count("route_places"))
            .order_by("-is_featured", "title")
        )

    @staticmethod
    def get_detail_queryset() -> QuerySet:
        from .models import TourRoute
        return (
            TourRoute.objects
            .filter(is_active=True)
            .prefetch_related(
                "route_places",
                "route_places__place",
                "route_places__place__category",
            )
            .annotate(stop_count=Count("route_places"))
        )

    @staticmethod
    def increment_view_count(route_id) -> None:
        from .models import TourRoute
        TourRoute.objects.filter(pk=route_id).update(view_count=F("view_count") + 1)