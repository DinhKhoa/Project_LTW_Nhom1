from django.urls import path
from . import views

app_name = 'warranty'

urlpatterns = [
    path('', views.warranty_view, name='warranty_view'),
]
