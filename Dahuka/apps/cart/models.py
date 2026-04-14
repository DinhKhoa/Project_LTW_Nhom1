from django.db import models
from django.contrib.auth.models import User
from apps.products.models import Product

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Giỏ hàng"
        verbose_name_plural = "Các giỏ hàng"

    def __str__(self):
        if self.user:
            return f"Cart of {self.user.username}"
        return f"Cart {self.session_key}"

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def selected_total_price(self):
        return sum(item.subtotal for item in self.items.filter(is_selected=True))

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=12, decimal_places=0) # Price at time of adding
    is_selected = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Sản phẩm trong giỏ"
        verbose_name_plural = "Sản phẩm trong giỏ hàng"

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

    @property
    def subtotal(self):
        return self.price * self.quantity
