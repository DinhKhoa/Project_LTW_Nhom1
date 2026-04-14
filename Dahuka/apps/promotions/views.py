from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Promotion

def promotion_detail(request):
    return render(request, 'promotions/promotion_detail.html')

def promotion_list(request):
    today = timezone.now().date()
    promotions_list = Promotion.objects.all().order_by('-start_date')
    
    # Calculate stats
    total_count = promotions_list.count()
    active_count = promotions_list.filter(is_active=True, start_date__lte=today, end_date__gte=today).count()
    upcoming_count = promotions_list.filter(is_active=True, start_date__gt=today).count()
    ended_count = total_count - active_count - upcoming_count
    
    paginator = Paginator(promotions_list, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'total_count': total_count,
        'active_count': active_count,
        'upcoming_count': upcoming_count,
        'ended_count': ended_count,
    }
    
    return render(request, 'promotions/promotion_list.html', context)

def add_promotion(request):
    # Simplified for now until forms are fully English-ized
    return render(request, "promotions/add_promotion.html")
