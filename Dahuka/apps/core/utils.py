from typing import Any, Optional
from django.http import HttpRequest
from django.core.paginator import Page, Paginator

# --- CÁC HÀM TIỆN ÍCH (HELPER FUNCTIONS) ---

def format_money(value: Optional[Any]) -> str:
    """Định dạng số thành chuỗi tiền tệ VN (Ví dụ: 1000000 -> 1.000.000)."""
    if value is None:
        return "0"
    try:
        return "{:,.0f}".format(float(value)).replace(",", ".")
    except (ValueError, TypeError):
        return "0"


def get_paginated_data(queryset: Any, request: HttpRequest, per_page: int) -> Page:
    """Hỗ trợ phân trang danh sách dữ liệu (Sản phẩm, Đơn hàng, v.v.)."""
    page_number = request.GET.get("page", 1) # Lấy số trang hiện tại từ URL
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(page_number)
