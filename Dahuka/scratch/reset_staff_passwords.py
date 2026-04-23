import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dahuka.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
users = ['dinhkhoa', 'truonggiang']

for username in users:
    try:
        u = User.objects.get(username=username)
        u.set_password('Staff@123')
        u.is_active = True
        u.is_staff = True
        u.save()
        print(f"Password and staff status updated for: {username}")
    except User.DoesNotExist:
        print(f"User {username} not found.")
