from django.utils import timezone
from django.db.models import Q
from .models import Promotion

class PromotionSelector:
    @staticmethod
    def get_promotion_stats():
        """
        Tính toán các thông số thống kê cho danh sách khuyến mãi.
        """
        today = timezone.localtime().date()
        all_promos = Promotion.objects.all()
        total_count = all_promos.count()
        active_count = all_promos.filter(is_active=True, start_date__lte=today, end_date__gte=today).count()
        upcoming_count = all_promos.filter(start_date__gt=today).count()
        ended_count = total_count - active_count - upcoming_count
        
        return {
            'total_count': total_count,
            'active_count': active_count,
            'upcoming_count': upcoming_count,
            'ended_count': ended_count,
        }

    @staticmethod
    def get_filtered_promotions(query=None, status=None):
        """
        Lọc danh sách khuyến mãi theo từ khóa và trạng thái.
        """
        today = timezone.localtime().date()
        queryset = Promotion.objects.all().order_by('id')
        
        if query:
            queryset = queryset.filter(Q(name__icontains=query) | Q(code__icontains=query))
            
        if status == 'active':
            queryset = queryset.filter(is_active=True, start_date__lte=today, end_date__gte=today)
        elif status == 'upcoming':
            queryset = queryset.filter(start_date__gt=today)
        elif status == 'ended':
            queryset = queryset.exclude(
                Q(is_active=True, start_date__lte=today, end_date__gte=today) |
                Q(start_date__gt=today)
            )
            
        return queryset
