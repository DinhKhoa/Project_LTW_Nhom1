from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import WarrantyPageSettings
from apps.orders.models import Order

def warranty_view(request):
    # Fetch or create settings
    settings = WarrantyPageSettings.objects.first()
    if not settings:
        settings = WarrantyPageSettings.objects.create()

    # Handle Admin Update (POST)
    if request.method == 'POST' and request.user.is_superuser:
        if 'image_one' in request.FILES:
            settings.image_one = request.FILES['image_one']
        if 'image_two' in request.FILES:
            settings.image_two = request.FILES['image_two']
        
        settings.save()
        messages.success(request, 'Đã cập nhật cấu hình trang bảo hành!')
        return redirect('warranty:warranty_view')

    # Search logic (by Order Code or Phone)
    query = request.GET.get('q', '').strip()
    results = None
    if query:
        # Search by order_code or customer phone
        results = Order.objects.filter(
            Q(order_code__iexact=query) | Q(phone=query)
        ).filter(status='completed').prefetch_related('items__product')
        
        if not results:
            messages.warning(request, f'Không tìm thấy thông tin bảo hành cho mã: {query}')

    return render(request, 'warranty.html', {
        'settings': settings,
        'results': results,
        'query': query
    })
