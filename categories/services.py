from .models import Category
from django.db.models import QuerySet

class CategoryService:
    @staticmethod
    def get_list_queryset() -> QuerySet:
        return Category.objects.filter(is_active=True).order_by("title")
