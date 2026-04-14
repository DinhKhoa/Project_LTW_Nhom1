from django.shortcuts import render

def index(request):
    return render(request, 'warranty/list.html')
