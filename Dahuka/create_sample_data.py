"""
Script to create sample data for testing
"""
import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dahuka.settings')
django.setup()

from django.contrib.auth.models import User
from trangchu.models import Customer, Address, Order, OrderItem

# Clear existing data (optional)
print("Creating test user...")

# Create test user if not exists
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'test@example.com',
        'first_name': 'An',
        'last_name': 'Nguyễn Văn'
    }
)

if created:
    user.set_password('password123')
    user.save()
    print(f"Created user: {user.username}")
else:
    print(f"User already exists: {user.username}")

# Create or get customer
customer, created = Customer.objects.get_or_create(
    user=user,
    defaults={'phone': '0934943950'}
)

if created:
    print(f"Created customer")

# Create sample addresses
print("Creating sample addresses...")
addresses = [
    {
        'full_name': 'An Nguyễn Văn',
        'phone': '0934943950',
        'email': 'an@example.com',
        'province': 'Thành phố Đà Nẵng',
        'district': 'Quận Sơn Trà',
        'ward': 'Phường Phước Mỹ',
        'address_detail': '68 Đường Khuê',
        'address_type': 'home',
        'is_default': True
    },
    {
        'full_name': 'Văn Nguyễn',
        'phone': '0912345678',
        'email': 'van@example.com',
        'province': 'Thành phố Hồ Chí Minh',
        'district': 'Quận 1',
        'ward': 'Phường Bến Nghé',
        'address_detail': '123 Đường Nguyễn Huệ',
        'address_type': 'office',
        'is_default': False
    }
]

for addr_data in addresses:
    addr, created = Address.objects.get_or_create(
        customer=customer,
        phone=addr_data['phone'],
        defaults=addr_data
    )
    if created:
        print(f"Created address for {addr_data['full_name']}")

# Create sample orders
print("Creating sample orders...")
orders = [
    {
        'order_number': 'DH20260122008',
        'total_amount': 11645000,
        'status': 'pending',
        'items': [
            {'product_name': 'Máy Lọc Nước RO 12 Cấp Mutosi MP-S126', 'quantity': 1, 'unit_price': 11645000}
        ]
    },
    {
        'order_number': 'DH20260122002',
        'total_amount': 5211000,
        'status': 'processing',
        'items': [
            {'product_name': 'Máy Lọc Nước Nóng Lạnh Mutosi', 'quantity': 1, 'unit_price': 5211000}
        ]
    },
    {
        'order_number': 'DH20260122001',
        'total_amount': 7900000,
        'status': 'completed',
        'items': [
            {'product_name': 'Máy Lọc Nước Ion Kiềm Hydrogen', 'quantity': 1, 'unit_price': 7900000}
        ]
    }
]

default_address = Address.objects.filter(customer=customer, is_default=True).first()

for order_data in orders:
    order, created = Order.objects.get_or_create(
        customer=customer,
        order_number=order_data['order_number'],
        defaults={
            'total_amount': order_data['total_amount'],
            'status': order_data['status'],
            'address': default_address
        }
    )
    
    if created:
        # Add items
        for item_data in order_data['items']:
            OrderItem.objects.create(
                order=order,
                **item_data
            )
        print(f"Created order {order_data['order_number']}")

print("Sample data creation completed!")
print(f"Test user: {user.username}")
print(f"Test password: password123")
print(f"Email: {user.email}")

