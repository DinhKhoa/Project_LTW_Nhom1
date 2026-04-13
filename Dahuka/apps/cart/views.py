from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse


# Helper function for formatting money
def format_money(value):
    return "{:,.0f}".format(value).replace(",", ".")


def cart(request):
    # Initialize session state if not present
    if 'checkout_state' not in request.session:
        request.session['checkout_state'] = {
            'current_screen': 'cart',
            'cart_payment_type': 'full',
            'order_method': 'bank',
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

    # Only reset to cart screen when navigating from outside (no referer from same cart)
    if request.method == 'GET':
        referer = request.META.get('HTTP_REFERER', '')
        cart_url = request.build_absolute_uri(reverse('cart:cart'))
        if not referer or not referer.startswith(cart_url.split('?')[0]):
            state['current_screen'] = 'cart'
            request.session.modified = True

    default_product = {
        'name': "Máy lọc nước điện giải ion kiềm Hydrogen MP-T888",
        'variant': "Tiêu chuẩn",
        'price': 5990000,
        'shipping_fee': 0
    }

    current_product = request.session.get('current_cart_product', default_product)
    if not current_product.get('price'):
        current_product = default_product

    product_name = current_product['name']
    product_variant = current_product['variant']
    base_price = current_product['price']
    shipping_fee = current_product['shipping_fee']

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

    if request.method == 'POST':
        action = request.POST.get('action')
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

        if action == 'update_customer':
            state['customer']['name'] = request.POST.get('customer_name', state['customer']['name']).strip()
            state['customer']['phone'] = request.POST.get('customer_phone', state['customer']['phone']).strip()
            state['customer']['email'] = request.POST.get('customer_email', state['customer'].get('email', '')).strip()
            state['customer']['city'] = request.POST.get('customer_city', state['customer']['city'])
            state['customer']['district'] = request.POST.get('customer_district', state['customer']['district'])
            state['customer']['ward'] = request.POST.get('customer_ward', state['customer']['ward'])
            state['customer']['street'] = request.POST.get('customer_street', state['customer']['street']).strip()
            request.session.modified = True
            request.session['message'] = 'Cập nhật địa chỉ thành công'
            return redirect(reverse('cart:cart'))

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
            state['current_screen'] = 'order'
            request.session.modified = True
            return redirect(reverse('cart:cart'))

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

    context = {
        'product_name': product_name,
        'product_variant': product_variant,
        'product_price': base_price,
        'shipping_fee': shipping_fee,
        'formatted_base_price': format_money(base_price),
        'formatted_shipping_fee': format_money(shipping_fee),
        'formatted_total_price': format_money(base_price + shipping_fee),
        'deposit_amount': deposit_amount,
        'formatted_deposit_amount': format_money(deposit_amount),
        'formatted_remaining_amount': format_money((base_price + shipping_fee) - deposit_amount),
        'state': state,
        'current_screen': state['current_screen'],
        'coupon_code': state.get('coupon_code', ''),
        'customer_full_address': f"{state['customer']['street']}, {state['customer']['ward']}, {state['customer']['district']}, Thành phố {state['customer']['city']}",
        'customer_formatted_phone': f"(+84) {state['customer']['phone']}",
    }

    if 'message' in request.session:
        context['message'] = request.session.pop('message')

    return render(request, 'cart/cart.html', context)


def add_product_to_cart(request):
    if request.method == 'GET':
        product_name = request.GET.get('name', "Sản phẩm không xác định")
        product_variant = request.GET.get('variant', "Mặc định")
        try:
            product_price = int(request.GET.get('price', 0))
        except ValueError:
            product_price = 0
        try:
            product_shipping_fee = int(request.GET.get('shipping_fee', 0))
        except ValueError:
            product_shipping_fee = 0

        request.session['current_cart_product'] = {
            'name': product_name,
            'variant': product_variant,
            'price': product_price,
            'shipping_fee': product_shipping_fee
        }
        request.session.modified = True
    return redirect(reverse('cart:cart'))
