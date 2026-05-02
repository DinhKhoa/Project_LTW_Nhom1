from django.db.models import QuerySet, Q
from .models import Category

def get_category_queryset() -> QuerySet:
    """
    Returns the base queryset for categories, ordered by ID.
    """
    return Category.objects.all().order_by("id")

def search_categories(query: str = "") -> QuerySet:
    """
    Filters categories based on a search query (name or slug).
    """
    qs = get_category_queryset()
    if query:
        qs = qs.filter(
            Q(name__icontains=query) | Q(slug__icontains=query)
        )
    return qs

def get_category_by_id(pk: int) -> Category:
    """
    Retrieves a single category by its primary key.
    """
    from django.shortcuts import get_object_or_404
    return get_object_or_404(Category, pk=pk)
