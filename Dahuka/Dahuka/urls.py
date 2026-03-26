from django.contrib import admin
from django.urls import path
import trangchu.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', trangchu.views.index, name='product_list'),
    path('product/<str:product_id>/', trangchu.views.product_detail, name='product_detail'),
]
