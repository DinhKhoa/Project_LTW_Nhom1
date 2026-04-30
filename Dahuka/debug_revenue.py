import os
import django
import sys
from django.db.models import Sum

# Setup Django environment
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dahuka.settings')
django.setup()

from apps.orders.models import Order

def debug_revenue():
    print("--- 2026 Monthly Revenue Check ---")
    orders = Order.objects.filter(status='completed', created_at__year=2026)
    for m in range(1, 6):
        total = orders.filter(created_at__month=m).aggregate(s=Sum('total_amount'))['s'] or 0
        count = orders.filter(created_at__month=m).count()
        print(f"Month {m}: {count} orders, Total: {total:,.0f}d")
    
    print("\n--- Detailed Check for April (Month 4) ---")
    april_orders = orders.filter(created_at__month=4)
    if april_orders.exists():
        first = april_orders.order_by('created_at').first()
        last = april_orders.order_by('created_at').last()
        print(f"First April Order: {first.created_at} - {first.total_amount:,.0f}d")
        print(f"Last April Order: {last.created_at} - {last.total_amount:,.0f}d")
    else:
        print("No April orders found via __month=4 filter!")

if __name__ == "__main__":
    debug_revenue()
