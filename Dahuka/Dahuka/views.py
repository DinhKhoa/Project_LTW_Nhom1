from django.shortcuts import render

def index(request):
    return render(request, 'base.html')


def login_admin(request):
    return render(request, 'login_admin.html')
