from django.db.models import QuerySet, Q
from .models import Category

def get_category_queryset() -> QuerySet:
    return Category.objects.all().order_by("id")

def search_categories(query: str = "") -> QuerySet:
    qs = get_category_queryset()
    if query:
        qs = qs.filter(
            Q(name__icontains=query) | Q(slug__icontains=query)
        )
    return qs

def get_category_by_id(pk: int) -> Category:
    from django.shortcuts import get_object_or_404
    return get_object_or_404(Category, pk=pk)
