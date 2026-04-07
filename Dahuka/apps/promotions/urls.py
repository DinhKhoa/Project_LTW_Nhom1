from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    path('chi-tiet/', views.chi_tiet_khuyen_mai, name='chi_tiet_khuyen_mai'),
]
