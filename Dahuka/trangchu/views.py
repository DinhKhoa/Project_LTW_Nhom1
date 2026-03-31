from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

# Helper function for formatting money
def format_money(value):
    return "{:,.0f}".format(value).replace(",", ".")

def index(request):
    return render(request, 'base.html')

def cart(request):
    # Initialize session state if not present
    if 'checkout_state' not in request.session:
        request.session['checkout_state'] = {
            'current_screen': 'cart', # 'cart', 'order', 'bank_payment', 'success'
            'cart_payment_type': 'full', # 'full' or 'deposit'
            'order_method': 'bank', # 'bank' or 'cod'
            'deposit_percent': 10,
            'coupon_code': '',
            'customer': {
                'name': 'Nguyễn Văn An',
                'phone': '0999666777',
                'email': 'VanAn123456@gmail.com',
                'city': 'Đà Nẵng',
                'district': 'Quận Ngũ Hành Sơn',
                'ward': 'Phường Hoà Quý',
                'street': '68 Đường Khuê'
            }
        }

    state = request.session['checkout_state']

    # --- Product details management ---
    # Default product if nothing is explicitly added to cart
    default_product = {
        'name': "Máy lọc nước điện giải ion kiềm Hydrogen MP-T888",
        'variant': "Loại: Tiêu chuẩn",
        'price': 5990000,
        'shipping_fee': 0
    }

    # Use product from session, or default if not set
    current_product = request.session.get('current_cart_product', default_product)

    product_name = current_product['name']
    product_variant = current_product['variant']
    base_price = current_product['price']
    shipping_fee = current_product['shipping_fee']
    # --- End product details management ---

    # Calculate deposit amount
    deposit_amount = round(base_price * state['deposit_percent'] / 100)

    def checkout_payload():
        current_deposit = round(base_price * state['deposit_percent'] / 100)
        return {
            'cart_payment_type': state['cart_payment_type'],
            'order_method': state['order_method'],
            'deposit_percent': state['deposit_percent'],
            'formatted_deposit_amount': format_money(current_deposit),
            'formatted_total_price': format_money(base_price + shipping_fee),
            'coupon_code': state.get('coupon_code', ''),
        }

    # Handle POST requests
    if request.method == 'POST':
        action = request.POST.get('action')
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

        if action == 'update_customer':
            state['customer']['name'] = request.POST.get('customer_name', state['customer']['name']).strip()
            state['customer']['phone'] = request.POST.get('customer_phone', state['customer']['phone']).strip()
            state['customer']['email'] = request.POST.get('customer_email', state['customer']['email']).strip()
            state['customer']['city'] = request.POST.get('customer_city', state['customer']['city'])
            state['customer']['district'] = request.POST.get('customer_district', state['customer']['district'])
            state['customer']['ward'] = request.POST.get('customer_ward', state['customer']['ward'])
            state['customer']['street'] = request.POST.get('customer_street', state['customer']['street']).strip()
            request.session.modified = True
            request.session['message'] = 'Cập nhật địa chỉ thành công'
            return redirect(reverse('cart'))

        elif action == 'update_deposit':
            try:
                delta = int(request.POST.get('deposit_delta', 0))
                if delta != 0:
                    new_deposit_percent = state['deposit_percent'] + delta
                else:
                    new_deposit_percent = int(request.POST.get('deposit_percent_input', state['deposit_percent']))
                state['deposit_percent'] = max(10, min(100, new_deposit_percent))
            except ValueError:
                pass
            request.session.modified = True
            if is_ajax:
                return JsonResponse({'ok': True, **checkout_payload()})
            return redirect(reverse('cart'))

        elif action == 'update_payment_type':
            new_payment_type = request.POST.get('cart_payment_type')
            if new_payment_type in ['full', 'deposit']:
                state['cart_payment_type'] = new_payment_type
                if state['cart_payment_type'] == 'full':
                    state['order_method'] = 'bank'
            request.session.modified = True
            if is_ajax:
                return JsonResponse({'ok': True, **checkout_payload()})
            return redirect(reverse('cart'))

        elif action == 'go_to_order':
            state['current_screen'] = 'order'
            request.session.modified = True
            return redirect(reverse('cart'))

        elif action == 'update_order_method':
            new_order_method = request.POST.get('order_method')
            if new_order_method in ['bank', 'cod']:
                if new_order_method == 'cod' and state['cart_payment_type'] == 'full':
                    request.session['message'] = 'Thanh toán toàn bộ thì không được chọn COD.'
                    state['order_method'] = 'bank'
                else:
                    state['order_method'] = new_order_method
            request.session.modified = True
            if is_ajax:
                return JsonResponse({'ok': True, **checkout_payload()})
            return redirect(reverse('cart'))

        elif action == 'apply_coupon':
            state['coupon_code'] = request.POST.get('coupon_code', '').strip().upper()
            request.session.modified = True
            if is_ajax:
                return JsonResponse({'ok': True, **checkout_payload()})
            return redirect(reverse('cart'))

        elif action == 'submit_order':
            if state['order_method'] == 'bank':
                state['current_screen'] = 'bank_payment'
            else:
                state['current_screen'] = 'success'
            request.session.modified = True
            return redirect(reverse('cart'))

        elif action == 'confirm_bank_payment':
            state['current_screen'] = 'success'
            request.session.modified = True
            return redirect(reverse('cart'))
        
        elif action == 'go_home_again' or action == 'shop_again':
            state['current_screen'] = 'cart'
            request.session.modified = True
            return redirect(reverse('cart'))

    # Prepare context for rendering
    context = {
        'product_name': product_name,
        'product_variant': product_variant,
        'product_price': base_price, # Pass raw price for JS calculations if any
        'shipping_fee': shipping_fee, # Pass raw shipping fee
        'formatted_base_price': format_money(base_price),
        'formatted_shipping_fee': format_money(shipping_fee),
        'formatted_total_price': format_money(base_price + shipping_fee),
        'deposit_amount': deposit_amount,
        'formatted_deposit_amount': format_money(deposit_amount),
        'state': state,
        'current_screen': state['current_screen'],
        'coupon_code': state.get('coupon_code', ''),
        'customer_full_address': f"{state['customer']['street']}, {state['customer']['ward']}, {state['customer']['district']}, Thành phố {state['customer']['city']}",
        'customer_formatted_phone': f"(+84) {state['customer']['phone']}",
    }

    if 'message' in request.session:
        context['message'] = request.session.pop('message')

    return render(request, 'cart.html', context)


def add_product_to_cart(request):
    if request.method == 'GET': # Using GET for simplicity to demonstrate, POST is generally better for data changes
        product_name = request.GET.get('name', "Sản phẩm không xác định")
        product_variant = request.GET.get('variant', "Loại: Mặc định")
        # Ensure price and shipping_fee are integers
        try:
            product_price = int(request.GET.get('price', 0))
        except ValueError:
            product_price = 0
        try:
            product_shipping_fee = int(request.GET.get('shipping_fee', 0))
        except ValueError:
            product_shipping_fee = 0

        new_product = {
            'name': product_name,
            'variant': product_variant,
            'price': product_price,
            'shipping_fee': product_shipping_fee
        }
        request.session['current_cart_product'] = new_product
        request.session.modified = True # Mark session as modified
    return redirect(reverse('cart'))