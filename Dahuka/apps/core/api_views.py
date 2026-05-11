from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from django.utils.dateformat import format
from .models import Notification

# --- API QUẢN LÝ THÔNG BÁO (NOTIFICATIONS) ---

@login_required
@require_GET
def fetch_notifications(request):
    """Lấy danh sách 10 thông báo mới nhất của người dùng hiện tại."""
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
            'created_at': format(notif.created_at, 'd/m/Y H:i'), # Định dạng ngày tháng VN
        })
        
    return JsonResponse({
        'status': 'success',
        'unread_count': unread_count,
        'notifications': data
    })

@login_required
@require_POST
def mark_notification_read(request, notif_id):
    """Đánh dấu một thông báo cụ thể là đã đọc."""
    try:
        notification = Notification.objects.get(id=notif_id, recipient=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Không tìm thấy thông báo'}, status=404)

@login_required
@require_POST
def mark_all_notifications_read(request):
    """Đánh dấu TẤT CẢ thông báo của người dùng là đã đọc."""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})

# --- API GỢI Ý TÌM KIẾM (SEARCH SUGGESTIONS) ---

@require_GET
def api_product_suggestions(request):
    """
    Gợi ý nhanh sản phẩm khi người dùng đang gõ từ khóa vào thanh tìm kiếm.
    Trả về: Tên, giá, ảnh và link chi tiết sản phẩm.
    """
    from apps.products.models import Product
    from django.urls import reverse
    
    query = request.GET.get('q', '').strip()
    if not query or len(query) < 2:
        return JsonResponse({'status': 'success', 'results': []})
    
    # Tìm kiếm sản phẩm theo tên (không phân biệt hoa thường)
    products = Product.objects.filter(
        name__icontains=query,
        is_active=True
    ).order_by('-id')[:8]
    
    results = []
    for p in products:
        results.append({
            'name': p.name,
            'price': f"{p.price:,.0f}đ".replace(',', '.'), # Định dạng tiền tệ VN
            'image': p.main_image_url,
            'url': reverse('core:view_product_detail', args=[p.slug])
        })
        
    return JsonResponse({
        'status': 'success',
        'results': results
    })
