from typing import Any, Optional
from django.http import HttpRequest
from django.core.paginator import Page, Paginator


def format_money(value: Optional[Any]) -> str:
    if value is None:
        return "0"
    try:
        return "{:,.0f}".format(float(value)).replace(",", ".")
    except (ValueError, TypeError):
        return "0"


def get_paginated_data(queryset: Any, request: HttpRequest, per_page: int) -> Page:
    page_number = request.GET.get("page", 1)
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(page_number)
