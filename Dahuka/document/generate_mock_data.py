import os
import django
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dahuka.settings')
django.setup()

from django.contrib.auth.models import User
from apps.products.models import Product
from apps.promotions.models import Promotion
from apps.orders.models import Order, OrderItem
from apps.cart.models import Cart, CartItem

def generate_data():
    print("Generating mock data...")

    # 1. Ensure at least one customer and one staff
    customer, _ = User.objects.get_or_create(username='khachhang1', defaults={'first_name': 'Khách', 'last_name': 'Hàng 1', 'email': 'kh@example.com'})
    customer.set_password('123456')
    customer.save()
    
    staff, _ = User.objects.get_or_create(username='nhanvien1', defaults={'first_name': 'Nhân', 'last_name': 'Viên 1', 'email': 'nv@example.com', 'is_staff': True})
    staff.set_password('123456')
    staff.save()

    tech, _ = User.objects.get_or_create(username='kythuat1', defaults={'first_name': 'Kỹ', 'last_name': 'Thuật 1', 'email': 'kt@example.com'})
    staff.set_password('123456')
    staff.save()
    
    products = list(Product.objects.all()[:10])
    if not products:
        print("Trống sản phẩm. Không thể tạo.")
        return

    # 2. Promotions
    Promotion.objects.all().delete()
    promo1 = Promotion.objects.create(
        name="Giảm giá mùa hè 10%",
        code="SUMMER10",
        condition="Áp dụng cho tất cả máy lọc nước",
        discount_type="percent",
        value=Decimal('10'),
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + timedelta(days=30),
        is_active=True
    )
    promo2 = Promotion.objects.create(
        name="Giảm trực tiếp 500k",
        code="GIAM500",
        condition="Áp dụng đơn hàng trên 5 triệu",
        discount_type="fixed",
        value=Decimal('500000'),
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + timedelta(days=15),
        is_active=True
    )
    promo1.products.set(products[:5])
    promo2.products.set(products[5:])
    print("Created 2 Promotions.")

    # 3. Orders
    Order.objects.all().delete()
    
    statuses = ['pending', 'confirmed', 'processing', 'completed', 'cancelled']
    for i in range(5):
        order = Order.objects.create(
            customer=customer,
            full_name=f"Nguyen Van {i}",
            phone=f"098765432{i}",
            address=f"{i} Street ABC",
            total_amount=Decimal('0'),
            status=statuses[i],
            assigned_staff=staff if statuses[i] != 'pending' else None
        )
        total = Decimal('0')
        for j in range(random.randint(1, 3)):
            p = random.choice(products)
            q = random.randint(1, 2)
            total += p.price * q
            OrderItem.objects.create(order=order, product=p, quantity=q, price=p.price)
        
        order.total_amount = total
        order.save()

    print("Created 5 Orders.")

    # 4. Cart
    Cart.objects.all().delete()
    cart = Cart.objects.create(user=customer)
    for _ in range(3):
        p = random.choice(products)
        q = random.randint(1, 2)
        CartItem.objects.create(cart=cart, product=p, quantity=q, price=p.price)
    
    print("Created Cart for khachhang1 with 3 items.")

if __name__ == '__main__':
    generate_data()
