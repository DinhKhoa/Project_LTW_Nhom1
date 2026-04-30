import os
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone
import pytz
import sys

# Setup Django environment
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dahuka.settings')
django.setup()

from django.contrib.auth.models import User
from apps.orders.models import Order, OrderItem
from apps.products.models import Product
from apps.account.models import Customer
from django.db import connection

def seed_realistic_data():
    vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
    print("Starting specialized seeding (Sep 2025 - Apr 2026)...")
    
    # 1. Cleanup EVERYTHING to avoid FK issues
    print("Cleaning all items and orders...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("PRAGMA foreign_keys = OFF;")
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            cursor.execute("PRAGMA foreign_keys = ON;")
        print("Cleanup successful.")
    except Exception as e:
        print(f"Cleanup failed: {e}")
        return

    # 2. Prepare Base Data
    products = list(Product.objects.filter(is_active=True))
    customers = list(Customer.objects.all())
    staff_members = list(User.objects.filter(is_staff=True, is_superuser=False))
    
    if not products or not customers or not staff_members:
        print("Error: Missing base data.")
        return

    # 3. Seed Orders
    start_range = vn_tz.localize(datetime(2025, 9, 1))
    end_range = vn_tz.localize(datetime(2026, 5, 1))
    current_date = start_range
    orders_created = 0
    
    while current_date < end_range:
        num_orders = random.choices([1, 2, 3], weights=[40, 40, 20])[0]
        
        for _ in range(num_orders):
            customer = random.choice(customers)
            staff = random.choice(staff_members)
            
            # Creation time
            order_hour = random.randint(0, 23)
            order_minute = random.randint(0, 59)
            created_at = current_date.replace(hour=order_hour, minute=order_minute)
            
            # Completion time (office hours 08:00 - 18:00)
            done_hour = random.randint(8, 17)
            done_minute = random.randint(0, 59)
            updated_at = current_date.replace(hour=done_hour, minute=done_minute)
            
            # Logic: If created late, complete next day
            if order_hour >= 18:
                updated_at = updated_at + timedelta(days=1)
                if updated_at >= end_range:
                    updated_at = end_range - timedelta(minutes=random.randint(1, 60))

            # Create Order
            order = Order.objects.create(
                customer=customer.user,
                full_name=f"{customer.user.last_name} {customer.user.first_name}",
                phone=customer.phone,
                status='completed',
                assigned_staff=staff,
                total_amount=0
            )
            
            # Add items
            num_items = random.choices([1, 2], weights=[90, 10])[0]
            order_total = 0
            selected_products = random.sample(products, min(num_items, len(products)))
            
            for product in selected_products:
                qty = 1
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=qty,
                    price=product.price
                )
                order_total += (product.price * qty)
            
            order.total_amount = order_total
            order.save()
            
            # Force timestamps
            Order.objects.filter(id=order.id).update(
                created_at=created_at,
                updated_at=updated_at
            )
            orders_created += 1
            
        current_date += timedelta(days=1)
        if current_date.day == 1:
            print(f"Finished seeding for {current_date.strftime('%m/%Y')}...")

    print(f"Success! Created {orders_created} realistic orders.")

if __name__ == "__main__":
    seed_realistic_data()
