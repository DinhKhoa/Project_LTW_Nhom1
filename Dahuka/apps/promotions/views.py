from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Promotion
from .forms import PromotionForm
from apps.core.utils import get_paginated_data
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.core.decorators import staff_required

@login_required
@staff_required
def promotion_list(request):
    today = timezone.now().date()
    promotions_list = Promotion.objects.all().order_by('id')
    
    # Calculate stats
    total_count = promotions_list.count()
    active_count = promotions_list.filter(is_active=True, start_date__lte=today, end_date__gte=today).count()
    upcoming_count = promotions_list.filter(is_active=True, start_date__gt=today).count()
    ended_count = total_count - active_count - upcoming_count
    
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
@staff_required
def add_promotion(request, pk=None):
    promotion = get_object_or_404(Promotion, pk=pk) if pk else None
    
    if request.method == "POST":
        form = PromotionForm(request.POST, request.FILES, instance=promotion)
        if form.is_valid():
            saved_promo = form.save()
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
@staff_required
def promotion_detail(request, pk):
    promotion = get_object_or_404(Promotion, pk=pk)
    return render(request, 'promotion_detail.html', {'promotion': promotion})
