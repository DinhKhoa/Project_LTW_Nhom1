from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from apps.products.models import Product
from apps.account.models import Customer, Address
from .models import Cart, CartItem
from .forms import CustomerInfoForm

# Helper function for formatting money
def format_money(value):
    if value is None:
        return "0"
    return "{:,.0f}".format(value).replace(",", ".")


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def cart(request):
    cart_obj = get_or_create_cart(request)
    
    # Reset session if it contains old hardcoded sample data
    if 'checkout_state' in request.session:
        old_state = request.session['checkout_state']
        if old_state.get('customer', {}).get('name') == 'Nguyễn Văn An':
            del request.session['checkout_state']
            request.session.modified = True
            
    # Initialize session state if not present
    if 'checkout_state' not in request.session:
        # Initial defaults
        customer_data = {
            'name': '',
            'phone': '',
            'email': '',
            'city': 'Đà Nẵng',
            'district': '',
            'ward': '',
            'street': ''
        }
        
        # Try to pull from DB if user is authenticated
        if request.user.is_authenticated:
            try:
                profile = request.user.customer
                customer_data['name'] = request.user.get_full_name() or request.user.username
                customer_data['phone'] = profile.phone
                customer_data['email'] = request.user.email
                
                # Try to get default address
                default_addr = profile.addresses.filter(is_default=True).first() or profile.addresses.first()
                if default_addr:
                    customer_data['name'] = default_addr.full_name
                    customer_data['phone'] = default_addr.phone
                    customer_data['email'] = default_addr.email
                    customer_data['city'] = default_addr.province
                    customer_data['district'] = default_addr.district
                    customer_data['ward'] = default_addr.ward
                    customer_data['street'] = default_addr.address_detail
            except Exception:
                pass

        request.session['checkout_state'] = {
            'current_screen': 'cart',
            'cart_payment_type': 'full',
            'order_method': 'bank',
            'deposit_percent': 10,
            'coupon_code': '',
            'customer': customer_data
        }

    state = request.session['checkout_state']

    # Handle screen navigation and Title/Breadcrumb sync
    current_screen = state.get('current_screen', 'cart')
    
    # Synchronization logic for Title and Breadcrumbs
    page_titles = {
        'cart': 'Giỏ hàng',
        'order': 'Xác nhận đơn hàng',
        'bank_payment': 'Thanh toán chuyển khoản',
        'success': 'Đặt hàng thành công'
    }
    
    display_title = page_titles.get(current_screen, 'Giỏ hàng')
    
    # Initial breadcrumbs
    breadcrumbs = [
        {'name': 'Trang chủ', 'url': '/'},
        {'name': display_title, 'url': None}
    ]

    # Only reset to cart screen when navigating from outside (no referer from same cart)
    if request.method == 'GET':
        referer = request.META.get('HTTP_REFERER', '')
        cart_url = request.build_absolute_uri(reverse('cart:cart'))
        if not referer or not referer.startswith(cart_url.split('?')[0]):
            state['current_screen'] = 'cart'
            request.session.modified = True
            current_screen = 'cart'
            display_title = 'Giỏ hàng'

    # Prepare context data
    cart_items = cart_obj.items.all().select_related('product')
    total_price = cart_obj.total_price
    shipping_fee = 0 # Could be calculated
    deposit_amount = round(float(total_price) * state['deposit_percent'] / 100)

    # Initialize Form with session data
    customer_form = CustomerInfoForm(initial={
        'customer_name': state['customer'].get('name'),
        'customer_phone': state['customer'].get('phone'),
        'customer_email': state['customer'].get('email'),
        'customer_city': state['customer'].get('city'),
        'customer_district': state['customer'].get('district'),
        'customer_ward': state['customer'].get('ward'),
        'customer_street': state['customer'].get('street'),
    })

    def checkout_payload():
        current_deposit = round(float(total_price) * state['deposit_percent'] / 100)
        return {
            'cart_payment_type': state['cart_payment_type'],
            'order_method': state['order_method'],
            'deposit_percent': state['deposit_percent'],
            'formatted_deposit_amount': format_money(current_deposit),
            'formatted_total_price': format_money(float(total_price) + shipping_fee),
            'coupon_code': state.get('coupon_code', ''),
        }

    if request.method == 'POST':
        action = request.POST.get('action')
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

        if action == 'update_customer':
            form = CustomerInfoForm(request.POST)
            if form.is_valid():
                state['customer']['name'] = form.cleaned_data['customer_name']
                state['customer']['phone'] = form.cleaned_data['customer_phone']
                state['customer']['email'] = form.cleaned_data['customer_email']
                state['customer']['city'] = form.cleaned_data['customer_city']
                state['customer']['district'] = form.cleaned_data['customer_district']
                state['customer']['ward'] = form.cleaned_data['customer_ward']
                state['customer']['street'] = form.cleaned_data['customer_street']
                request.session.modified = True
                messages.success(request, 'Cập nhật tin nhận hàng thành công')
                return redirect(reverse('cart:cart'))
            else:
                customer_form = form

        elif action == 'update_deposit':
            try:
                new_val = request.POST.get('deposit_percent_input')
                if new_val is not None:
                    new_deposit_percent = int(new_val)
                else:
                    delta = int(request.POST.get('deposit_delta', 0))
                    new_deposit_percent = state['deposit_percent'] + delta
                state['deposit_percent'] = max(10, min(50, new_deposit_percent))
            except (ValueError, TypeError):
                pass
            request.session.modified = True
            if is_ajax:
                return JsonResponse({'ok': True, **checkout_payload()})
            return redirect(reverse('cart:cart'))

        elif action == 'update_payment_type':
            new_payment_type = request.POST.get('cart_payment_type')
            if new_payment_type in ['full', 'deposit']:
                state['cart_payment_type'] = new_payment_type
                if state['cart_payment_type'] == 'full':
                    state['order_method'] = 'bank'
            request.session.modified = True
            if is_ajax:
                return JsonResponse({'ok': True, **checkout_payload()})
            return redirect(reverse('cart:cart'))

        elif action == 'go_to_order':
            if not state['customer']['name'] or not state['customer']['phone']:
                messages.warning(request, "Vui lòng nhập thông tin nhận hàng")
                return redirect(reverse('cart:cart'))
            state['current_screen'] = 'order'
            request.session.modified = True
            return redirect(reverse('cart:cart'))

        elif action == 'update_order_method':
            new_order_method = request.POST.get('order_method')
            if new_order_method in ['bank', 'cod']:
                if new_order_method == 'cod' and state['cart_payment_type'] == 'full':
                    messages.error(request, 'Thanh toán toàn bộ thì không được chọn COD.')
                    state['order_method'] = 'bank'
                else:
                    state['order_method'] = new_order_method
            request.session.modified = True
            if is_ajax:
                return JsonResponse({'ok': True, **checkout_payload()})
            return redirect(reverse('cart:cart'))

        elif action == 'apply_coupon':
            state['coupon_code'] = request.POST.get('coupon_code', '').strip().upper()
            request.session.modified = True
            if is_ajax:
                return JsonResponse({'ok': True, **checkout_payload()})
            return redirect(reverse('cart:cart'))

        elif action == 'submit_order':
            if state['order_method'] == 'bank' or state['cart_payment_type'] == 'deposit':
                state['current_screen'] = 'bank_payment'
            else:
                state['current_screen'] = 'success'
            request.session.modified = True
            return redirect(reverse('cart:cart'))

        elif action == 'confirm_bank_payment':
            state['current_screen'] = 'success'
            request.session.modified = True
            return redirect(reverse('cart:cart'))

        elif action in ('go_home_again', 'shop_again'):
            state['current_screen'] = 'cart'
            request.session.modified = True
            return redirect(reverse('cart:cart'))

    # Build address string for display
    customer = state['customer']
    addr_parts = [
        customer.get('street', ''),
        customer.get('ward', ''),
        customer.get('district', ''),
        customer.get('city', '')
    ]
    customer_full_address = ", ".join([p for p in addr_parts if p])
    
    from datetime import datetime, timedelta
    delivery_date = (datetime.now() + timedelta(days=3)).strftime("%d/%m")
    
    context = {
        'cart': cart_obj,
        'cart_items': cart_items,
        'total_price': total_price,
        'shipping_fee': shipping_fee,
        'formatted_total_price': format_money(float(total_price) + shipping_fee),
        'deposit_amount': deposit_amount,
        'formatted_deposit_amount': format_money(deposit_amount),
        'formatted_remaining_amount': format_money((float(total_price) + shipping_fee) - deposit_amount),
        'state': state,
        'current_screen': current_screen,
        'display_title': display_title,
        'breadcrumbs': breadcrumbs,
        'coupon_code': state.get('coupon_code', ''),
        'customer_full_address': customer_full_address,
        'customer_formatted_phone': f"(+84) {customer['phone']}" if customer['phone'] else "",
        'customer_form': customer_form,
        'delivery_date': delivery_date,
    }

    return render(request, 'cart/cart.html', context)


def add_product_to_cart(request):
    product_id = request.GET.get('product_id')
    variant = request.GET.get('variant', "Mặc định")
    quantity = int(request.GET.get('quantity', 1))
    
    if product_id:
        product = get_object_or_404(Product, id=product_id)
        cart = get_or_create_cart(request)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, 
            product=product,
            variant=variant,
            defaults={'price': product.price, 'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
            
        messages.success(request, f"Đã thêm {product.name} vào giỏ hàng")
        
    return redirect(reverse('cart:cart'))


def delete_cart_item(request, item_id):
    cart = get_or_create_cart(request)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    messages.success(request, "Đã xóa sản phẩm khỏi giỏ hàng")
    return redirect(reverse('cart:cart'))
