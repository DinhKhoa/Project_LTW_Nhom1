import os
import django
import random
import sys

# Setup Django environment
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dahuka.settings')
django.setup()

from apps.orders.models import Order, OrderItem
from apps.products.models import Product

def restore_data():
    print("Starting Emergency Restoration...")
    products = list(Product.objects.filter(is_active=True))
    if not products:
        print("No products found.")
        return

    orders = Order.objects.all()
    restored = 0
    for o in orders:
        if o.items.count() == 0:
            product = random.choice(products)
            OrderItem.objects.create(
                order=o,
                product=product,
                quantity=1,
                price=product.price
            )
            restored += 1
    
    print(f"Successfully restored products for {restored} orders.")

if __name__ == "__main__":
    restore_data()
