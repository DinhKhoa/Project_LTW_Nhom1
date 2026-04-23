"""
Services for cart module.
Put business logic here to keep views lean.
"""
from django.db import transaction
from django.contrib.auth.models import User
from apps.orders.services import OrderService
from apps.promotions.models import Promotion


class CartService:
    """Service class for cart operations and order creation"""
    
    @staticmethod
    def create_order_from_cart(user, cart_obj, customer_data, order_items_data, coupon_code="", payment_type="full", order_method="bank"):
        """
        Create an order from cart items.
        """
        with transaction.atomic():
            if not order_items_data:
                raise ValueError("Giỏ hàng của bạn không có sản phẩm nào được chọn.")
            
            # Calculate discount if coupon exists
            discount_amount = 0
            if coupon_code:
                from django.utils import timezone
                promotion = Promotion.objects.filter(
                    code__iexact=coupon_code, 
                    is_active=True,
                    start_date__lte=timezone.now().date(),
                    end_date__gte=timezone.now().date()
                ).first()
                
                if promotion:
                    base_total = sum(item["price"] * item.get("quantity", 1) for item in order_items_data)
                    discount_amount = promotion.calculate_discount(base_total)
            
            # Create order via OrderService with split address fields
            try:
                order = OrderService.create_order(
                    customer=user,
                    full_name=customer_data.get('name'),
                    phone=customer_data.get('phone'),
                    cart_items=order_items_data,
                    city=customer_data.get('city', ''),
                    district=customer_data.get('district', ''),
                    ward=customer_data.get('ward', ''),
                    house_details=customer_data.get('street', ''),
                    discount_amount=discount_amount,
                    hinh_thuc_thanh_toan='chuyen_khoan' if order_method == 'bank' else 'tien_mat',
                    trang_thai_thanh_toan='da_thanh_toan' if payment_type == 'full' and order_method == 'bank' else 'chua_thanh_toan'
                )
                return order
            except Exception as e:
                raise ValueError(f"Lỗi tạo đơn hàng: {str(e)}")
    
    @staticmethod
    def get_cart_totals(cart_obj):
        """
        Calculate cart totals with better query efficiency.
        """
        from django.db.models import Sum, F
        
        totals = cart_obj.items.aggregate(
            total=Sum(F('price') * F('quantity'), output_field=None)
        )
        total_price = totals['total'] or 0
        shipping_fee = 0 
        
        return {
            'total_price': total_price,
            'shipping_fee': shipping_fee,
            'final_total': total_price + shipping_fee,
        }
