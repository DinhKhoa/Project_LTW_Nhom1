from django.urls import path
from . import views

app_name = 'warranty'

urlpatterns = [
    path('lookup/', views.warranty_lookup, name='index'),
    path('detail/<str:serial_number>/', views.warranty_detail, name='warranty_detail'),
]
