"""
favorites/views.py
==================
Endpoints:
  GET  /favorites/         — my saved places
  POST /favorites/toggle/  — add or remove a favorite
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import FavoriteSerializer, FavoriteToggleSerializer
from .services import FavoriteService


class FavoriteListView(generics.ListAPIView):
    """GET /favorites/ — paginated list of the current user's favorites."""
    serializer_class   = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FavoriteService.get_user_favorites(self.request.user)


class FavoriteToggleView(APIView):
    """
    POST /favorites/toggle/
    Body: { "place_id": "<uuid>" }
    Response: { "status": "added" | "removed", "place_id": "<uuid>" }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = FavoriteToggleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = FavoriteService.toggle(
            user=request.user,
            place_id=serializer.validated_data["place_id"],
        )
        return Response(result, status=status.HTTP_200_OK)