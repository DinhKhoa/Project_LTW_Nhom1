import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dahuka.settings')
django.setup()

from apps.categories.models import Category

cats = Category.objects.all()
print(f"Total categories: {cats.count()}")
for cat in cats:
    # Use ASCII or just IDs to avoid encoding issues in print
    print(f"ID: {cat.id}, Code: {cat.code}")
