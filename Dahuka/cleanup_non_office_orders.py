import os
import django
import sys
from datetime import datetime
import pytz

# Setup Django
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dahuka.settings')
django.setup()

from apps.orders.models import Order
from django.utils import timezone

def cleanup_orders():
    print("Starting office hours cleanup...")
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    orders = Order.objects.filter(status='completed')
    deleted_count = 0
    
    for o in orders:
        # Convert UTC to VN time
        local_dt = o.created_at.astimezone(vn_tz)
        
        # Check if outside 08:00 - 18:00
        if local_dt.hour < 8 or local_dt.hour >= 18:
            o.delete()
            deleted_count += 1
            
    print(f"Finished! Deleted {deleted_count} orders created outside office hours.")

if __name__ == "__main__":
    cleanup_orders()
