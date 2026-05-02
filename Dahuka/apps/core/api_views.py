from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from django.utils.dateformat import format
from .models import Notification

@login_required
@require_GET
def fetch_notifications(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:10]
    unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    
    data = []
    for notif in notifications:
        data.append({
            'id': notif.id,
            'title': notif.title,
            'message': notif.message,
            'link': notif.link,
            'is_read': notif.is_read,
            'created_at': format(notif.created_at, 'd/m/Y H:i'),
        })
        
    return JsonResponse({
        'status': 'success',
        'unread_count': unread_count,
        'notifications': data
    })

@login_required
@require_POST
def mark_notification_read(request, notif_id):
    try:
        notification = Notification.objects.get(id=notif_id, recipient=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Notification not found'}, status=404)

@login_required
@require_POST
def mark_all_notifications_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})

@require_GET
def api_product_suggestions(request):
    from apps.products.models import Product
    from django.urls import reverse
    
    query = request.GET.get('q', '').strip()
    if not query or len(query) < 2:
        return JsonResponse({'status': 'success', 'results': []})
    
    
    products = Product.objects.filter(
        name__icontains=query,
        is_active=True
    ).order_by('-id')[:8]
    
    results = []
    for p in products:
        results.append({
            'name': p.name,
            'price': f"{p.price:,.0f}đ".replace(',', '.'),
            'image': p.main_image_url,
            'url': reverse('core:view_product_detail', args=[p.slug])
        })
        
    return JsonResponse({
        'status': 'success',
        'results': results
    })
