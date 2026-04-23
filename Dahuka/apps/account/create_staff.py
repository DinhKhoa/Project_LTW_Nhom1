import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Dahuka.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

staff_data = [
    {
        'username': 'dinhkhoa',
        'email': 'dinhkhoa@dahuka.com',
        'first_name': 'Khoa',
        'last_name': 'Nguyễn Đình',
        'password': 'Staff@123'
    },
    {
        'username': 'truonggiang',
        'email': 'truonggiang@dahuka.com',
        'first_name': 'Giang',
        'last_name': 'Nguyễn Trường',
        'password': 'Staff@123'
    }
]

for data in staff_data:
    user, created = User.objects.get_or_create(
        username=data['username'],
        defaults={
            'email': data['email'],
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'is_staff': True
        }
    )
    if created:
        user.set_password(data['password'])
        user.save()
        print(f"Created staff user: {data['username']}")
    else:
        # Update existing user to be staff if not already
        user.is_staff = True
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.set_password(data['password'])
        user.save()
        print(f"Updated staff user: {data['username']}")
