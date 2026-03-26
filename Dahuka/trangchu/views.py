from django.shortcuts import render

def index(request):
    return render(request, 'product_list.html')

def product_detail(request, product_id):
    return render(request, 'product_detail.html')
