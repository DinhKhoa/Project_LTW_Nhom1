from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Promotion
from .forms import PromotionForm
from apps.core.utils import get_paginated_data
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.core.decorators import admin_required

@login_required
@admin_required
def promotion_list(request):
    today = timezone.localtime().date()
    promotions_list = Promotion.objects.all().order_by('id')
    
    # Calculate stats (Current logic: Upcoming is purely date-based)
    total_count = promotions_list.count()
    active_count = promotions_list.filter(is_active=True, start_date__lte=today, end_date__gte=today).count()
    upcoming_count = promotions_list.filter(start_date__gt=today).count()
    ended_count = total_count - active_count - upcoming_count

    # Apply search filter
    query = request.GET.get('q', '')
    if query:
        from django.db.models import Q
        promotions_list = promotions_list.filter(
            Q(name__icontains=query) | Q(code__icontains=query)
        )
    
    # Apply status filter
    status = request.GET.get('status', '')
    if status == 'active':
        promotions_list = promotions_list.filter(is_active=True, start_date__lte=today, end_date__gte=today)
    elif status == 'upcoming':
        promotions_list = promotions_list.filter(start_date__gt=today)
    elif status == 'ended':
        from django.db.models import Q
        promotions_list = promotions_list.exclude(
            Q(is_active=True, start_date__lte=today, end_date__gte=today) |
            Q(start_date__gt=today)
        )
    
    # Use centralized pagination
    page_obj = get_paginated_data(promotions_list, request, 10)
    
    context = {
        'page_obj': page_obj,
        'total_count': total_count,
        'active_count': active_count,
        'upcoming_count': upcoming_count,
        'ended_count': ended_count,
    }
    
    return render(request, 'promotion_list.html', context)

@login_required
@admin_required
def add_promotion(request, pk=None):
    promotion = get_object_or_404(Promotion, pk=pk) if pk else None
    
    if request.method == "POST":
        form = PromotionForm(request.POST, request.FILES, instance=promotion)
        if form.is_valid():
            saved_promo = form.save()
            
            # Gửi thông báo nếu khuyến mãi đang hoạt động, bắt đầu từ hôm nay/quá khứ và CHƯA GỬI
            today = timezone.localtime().date()
            if saved_promo.is_active and saved_promo.start_date <= today and not saved_promo.notification_sent:
                from django.contrib.auth.models import User
                from apps.core.services import CoreService
                
                customers = User.objects.filter(is_superuser=False, is_staff=False)
                for customer in customers:
                    CoreService.create_notification(
                        recipient=customer,
                        title="Khuyến mãi đang diễn ra!",
                        message=f"Chương trình '{saved_promo.name}' đã chính thức bắt đầu. Đừng bỏ lỡ!",
                        link=reverse('promotions:promotion_detail', args=[saved_promo.id])
                    )
                
                # Đánh dấu đã gửi
                saved_promo.notification_sent = True
                saved_promo.save(update_fields=['notification_sent'])

            messages.success(request, f'Đã {"cập nhật" if pk else "thêm mới"} chương trình khuyến mãi thành công!')
            return redirect('promotions:promotion_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = PromotionForm(instance=promotion)
    
    return render(request, "add_promotion.html", {
        'form': form,
        'is_edit': pk is not None
    })

@login_required
@admin_required
def promotion_detail(request, pk):
    promotion = get_object_or_404(Promotion, pk=pk)
    return render(request, 'promotion_detail.html', {'promotion': promotion})

@login_required
@admin_required
def delete_promotion(request, pk):
    promotion = get_object_or_404(Promotion, pk=pk)
    if request.method == "POST":
        name = promotion.name
        promotion.delete()
        messages.success(request, f'Đã xóa chương trình khuyến mãi "{name}" thành công.')
    return redirect('promotions:promotion_list')

from django.http import JsonResponse
from django.urls import reverse

def api_promotion_detail(request, pk):
    promotion = get_object_or_404(Promotion, pk=pk)
    
    products_data = []
    for product in promotion.products.all():
        products_data.append({
            'name': product.name,
            'sku': product.sku,
            'image': product.image.url if product.image else '/static/img/product-placeholder.png',
            'price': f"{product.price:,.0f}đ",
            'url': reverse('core:view_product_detail', args=[product.slug])
        })
        
    discount_display = f"{promotion.value:,.0f}%" if promotion.discount_type == 'percent' else f"{promotion.value:,.0f}đ"
    
    return JsonResponse({
        'status': 'success',
        'name': promotion.name,
        'code': promotion.code,
        'discount_display': discount_display,
        'description': getattr(promotion, 'description', 'Ưu đãi đặc biệt cho dòng sản phẩm của Dahuka.'),
        'condition': f"{promotion.condition:,.0f}",
        'products': products_data
    })
