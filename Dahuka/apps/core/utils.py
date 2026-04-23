from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from apps.core.constants import DEFAULT_PAGE_SIZE

def get_paginated_data(queryset, request, per_page=None):
    """
    Hàm tiện ích để phân trang cho bất kỳ queryset nào.
    Trả về page_obj đã được phân trang dựa trên tham số 'page' từ request.
    """
    if per_page is None:
        per_page = DEFAULT_PAGE_SIZE
    page_number = request.GET.get('page', 1)
    paginator = Paginator(queryset, per_page)
    
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
        
    return page_obj
