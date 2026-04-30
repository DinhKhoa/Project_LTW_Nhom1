from typing import Any, Optional
from django.http import HttpRequest
from django.core.paginator import Page, Paginator


def format_money(value: Optional[Any]) -> str:
    """
    Formats a numeric value into a currency string format (VND style).

    Args:
        value: The numeric value to format.

    Returns:
        A string formatted as "1.000.000".
    """
    if value is None:
        return "0"
    try:
        return "{:,.0f}".format(float(value)).replace(",", ".")
    except (ValueError, TypeError):
        return "0"


def get_paginated_data(queryset: Any, request: HttpRequest, per_page: int) -> Page:
    """
    Standard pagination utility for Dahuka project.

    Args:
        queryset: The queryset or list to paginate.
        request: The current HttpRequest.
        per_page: Number of items per page.

    Returns:
        A Django Page object.
    """
    page_number = request.GET.get("page", 1)
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(page_number)
