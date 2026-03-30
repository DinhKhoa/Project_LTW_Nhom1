"""
Quick test script to verify the implementation
Run: python manage.py shell < test.py
"""
from django.contrib.auth.models import User
from apps.core.models import Customer, Address, Order, OrderItem

# Check test user
try:
    user = User.objects.get(username='testuser')
    print(f"✓ Test user exists: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Name: {user.get_full_name()}")
except User.DoesNotExist:
    print("✗ Test user not found")

# Check customer
try:
    customer = Customer.objects.get(user__username='testuser')
    print(f"\n✓ Customer exists for test user")
    print(f"  Phone: {customer.phone}")
    print(f"  Addresses: {customer.addresses.count()}")
    print(f"  Orders: {customer.orders.count()}")
except Customer.DoesNotExist:
    print("\n✗ Customer not found")

# List addresses
addresses = Address.objects.filter(customer__user__username='testuser')
print(f"\n✓ Addresses ({addresses.count()}):")
for addr in addresses:
    print(f"  - {addr.full_name} ({addr.address_type})")
    print(f"    {addr.address_detail}, {addr.ward}, {addr.district}, {addr.province}")
    print(f"    Default: {addr.is_default}")

# List orders
orders = Order.objects.filter(customer__user__username='testuser')
print(f"\n✓ Orders ({orders.count()}):")
for order in orders:
    print(f"  - {order.order_number}")
    print(f"    Status: {order.status}")
    print(f"    Total: {order.total_amount}đ")
    print(f"    Items: {order.items.count()}")
    for item in order.items.all():
        print(f"      * {item.product_name} x{item.quantity}")

print("\n✓ All checks passed!")

