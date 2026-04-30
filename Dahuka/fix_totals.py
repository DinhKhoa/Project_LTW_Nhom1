import os
import django
import sys
from django.db.models import Sum, F

# Setup Django environment
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dahuka.settings')
django.setup()

from apps.orders.models import Order

def fix_totals():
    print("Fixing order totals to match items...")
    orders = Order.objects.all()
    count = 0
    for o in orders:
        total = o.items.aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0
        Order.objects.filter(id=o.id).update(total_amount=total)
        count += 1
    
    print(f"Successfully updated totals for {count} orders.")

if __name__ == "__main__":
    fix_totals()
