from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from .selectors import get_warranty_settings, search_warranty_orders
from .services import WarrantyService

def warranty_view(request: HttpRequest) -> HttpResponse:
    """
    Main view for the warranty page.
    Handles both display, search, and administrative updates.
    """
    settings = get_warranty_settings()

    # Handle Admin Update (Superuser only)
    if request.method == 'POST':
        if request.user.is_superuser:
            WarrantyService.update_settings(request.FILES)
            messages.success(request, 'Đã cập nhật cấu hình trang bảo hành!')
            return redirect('warranty:warranty_view')
        else:
            messages.error(request, 'Bạn không có quyền thực hiện thao tác này.')

    # Search logic
    query = request.GET.get('q', '').strip()
    results = search_warranty_orders(query)
    
    if query and not results:
        messages.warning(request, f'Không tìm thấy thông tin bảo hành cho mã: {query}')

    return render(request, 'warranty.html', {
        'settings': settings,
        'results': results,
        'query': query
    })
