from django.shortcuts import render, get_object_or_404
from .models import WarrantyCard, MaintenanceHistory
from django.db.models import Q
from django.contrib import messages

def warranty_lookup(request):
    query = request.GET.get('q')
    results = None
    if query:
        # Tra cứu theo Serial hoặc Số điện thoại (thông qua Profile Customer)
        results = WarrantyCard.objects.filter(
            Q(serial_number__iexact=query) | 
            Q(customer__customer__phone__icontains=query) |
            Q(customer__username__icontains=query)
        )
        if not results.exists():
            messages.warning(request, f"Không tìm thấy thông tin bảo hành cho: {query}")
        elif results.count() == 1:
            # Nếu chỉ có 1 kết quả, redirect thẳng vào chi tiết
            from django.shortcuts import redirect
            return redirect('warranty:warranty_detail', serial_number=results.first().serial_number)
            
    return render(request, 'warranty/lookup.html', {
        'results': results, 
        'query': query
    })

def warranty_detail(request, serial_number):
    card = get_object_or_404(WarrantyCard, serial_number=serial_number)
    logs = card.maintenance_logs.all().order_by('-date')
    return render(request, 'warranty/detail.html', {
        'card': card, 
        'logs': logs
    })
