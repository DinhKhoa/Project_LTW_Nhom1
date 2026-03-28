import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from trangchu.forms import AddressForm, CancelOrderForm, CustomerForm, PasswordChangeForm
from trangchu.models import Address, Customer, Order, OrderItem

def _get_or_create_customer(user):
    customer, _ = Customer.objects.get_or_create(user=user)
    return customer

@login_required(login_url='/login/')
def account_dashboard(request):
    section = request.GET.get('section', 'profile')
    if section == 'orders':
        return redirect('order_list')
    if section == 'addresses':
        return redirect('address_list')
    return redirect('profile_view')

@login_required
def address_list(request):
    customer = _get_or_create_customer(request.user)
    addresses = Address.objects.filter(customer=customer).order_by('-is_default', '-updated_at')
    return render(
        request,
        'account/addresses.html',
        {
            'addresses': addresses,
            'customer': customer,
            'active_section': 'addresses',
        },
    )

@login_required
def add_address(request):
    customer = _get_or_create_customer(request.user)

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.customer = customer
            if not Address.objects.filter(customer=customer).exists():
                address.is_default = True
            elif form.cleaned_data.get('is_default'):
                Address.objects.filter(customer=customer).update(is_default=False)
            address.save()
            messages.success(request, 'Thêm địa chỉ thành công')
            return redirect('address_list')
    else:
        form = AddressForm(initial={'address_type': 'home'})

    return render(
        request,
        'account/address_form.html',
        {
            'form': form,
            'title': 'Thêm địa chỉ',
            'customer': customer,
            'submit_label': 'Xác nhận',
        },
    )

@login_required
def edit_address(request, pk):
    customer = _get_or_create_customer(request.user)
    address = get_object_or_404(Address, id=pk, customer=customer)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            updated_address = form.save(commit=False)
            if form.cleaned_data.get('is_default'):
                Address.objects.filter(customer=customer).exclude(id=address.id).update(is_default=False)
            updated_address.save()
            messages.success(request, 'Cập nhật địa chỉ thành công')
            return redirect('address_list')
    else:
        form = AddressForm(instance=address)

    return render(
        request,
        'account/address_form.html',
        {
            'form': form,
            'title': 'Thông tin khách hàng',
            'customer': customer,
            'address': address,
            'submit_label': 'Cập nhật',
        },
    )

@login_required
def delete_address(request, pk):
    customer = _get_or_create_customer(request.user)
    address = get_object_or_404(Address, id=pk, customer=customer)

    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Xóa địa chỉ thành công')
        return redirect('address_list')

    return render(
        request,
        'account/delete_address.html',
        {
            'address': address,
            'customer': customer,
        },
    )

@login_required
def profile_view(request):
    customer = _get_or_create_customer(request.user)

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, 'Lưu thông tin thành công')
            return redirect('profile_view')
    else:
        form = CustomerForm(
            initial={
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
                'phone': customer.phone,
            },
            instance=customer,
        )

    return render(
        request,
        'account/profile.html',
        {
            'form': form,
            'customer': customer,
            'active_section': 'profile',
        },
    )

@login_required
def change_password(request):
    form = PasswordChangeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        if request.user.check_password(form.cleaned_data['old_password']):
            request.user.set_password(form.cleaned_data['new_password'])
            request.user.save()
            messages.success(request, 'Cập nhật mật khẩu thành công')
            return redirect('profile_view')
        messages.error(request, 'Mật khẩu cũ không đúng')

    return render(
        request,
        'account/change_password.html',
        {
            'form': form,
            'customer': _get_or_create_customer(request.user),
        },
    )

@login_required
def order_list(request):
    customer = _get_or_create_customer(request.user)
    orders = Order.objects.filter(customer=customer).select_related('address').order_by('-created_at')
    return render(
        request,
        'account/orders.html',
        {
            'orders': orders,
            'customer': customer,
            'active_section': 'orders',
        },
    )

@login_required
def order_detail(request, pk):
    customer = _get_or_create_customer(request.user)
    order = get_object_or_404(Order, id=pk, customer=customer)
    items = OrderItem.objects.filter(order=order)
    return render(
        request,
        'account/order_detail.html',
        {
            'order': order,
            'items': items,
            'customer': customer,
            'active_section': 'orders',
        },
    )

@login_required
def cancel_order(request, pk):
    customer = _get_or_create_customer(request.user)
    order = get_object_or_404(Order, id=pk, customer=customer)

    if order.status not in ['pending', 'processing']:
        messages.error(request, 'Không thể hủy đơn hàng ở trạng thái này')
        return redirect('order_detail', pk=pk)

    form = CancelOrderForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        order.status = 'cancelled'
        order.cancel_reason = form.cleaned_data['cancel_reason']
        order.save()
        messages.success(request, 'Hủy đơn hàng thành công')
        return redirect('order_detail', pk=pk)

    return render(
        request,
        'account/cancel_order.html',
        {
            'form': form,
            'order': order,
            'customer': customer,
            'active_section': 'orders',
        },
    )

@csrf_exempt
@require_http_methods(["GET", "POST", "PUT", "DELETE"])
@login_required
def api_addresses(request, pk=None):
    customer = _get_or_create_customer(request.user)

    if request.method == 'GET':
        if pk:
            try:
                address = Address.objects.get(id=pk, customer=customer)
            except Address.DoesNotExist:
                return JsonResponse({'error': 'Address not found'}, status=404)
            return JsonResponse(
                {
                    'id': address.id,
                    'full_name': address.full_name,
                    'phone': address.phone,
                    'email': address.email,
                    'province': address.province,
                    'district': address.district,
                    'ward': address.ward,
                    'address_type': address.address_type,
                    'address_detail': address.address_detail,
                    'is_default': address.is_default,
                }
            )

        addresses = Address.objects.filter(customer=customer).order_by('-is_default', '-updated_at')
        return JsonResponse(
            {
                'addresses': [
                    {
                        'id': addr.id,
                        'full_name': addr.full_name,
                        'phone': addr.phone,
                        'email': addr.email,
                        'province': addr.province,
                        'district': addr.district,
                        'ward': addr.ward,
                        'address_type': addr.address_type,
                        'address_detail': addr.address_detail,
                        'is_default': addr.is_default,
                    }
                    for addr in addresses
                ]
            }
        )

    if request.method == 'POST':
        data = json.loads(request.body)
        form = AddressForm(data)
        if form.is_valid():
            address = form.save(commit=False)
            address.customer = customer
            if not Address.objects.filter(customer=customer).exists():
                address.is_default = True
            elif form.cleaned_data.get('is_default'):
                Address.objects.filter(customer=customer).update(is_default=False)
            address.save()
            return JsonResponse({'success': True, 'message': 'Thêm địa chỉ thành công'})
        return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)

    if request.method == 'PUT' and pk:
        try:
            address = Address.objects.get(id=pk, customer=customer)
        except Address.DoesNotExist:
            return JsonResponse({'error': 'Address not found'}, status=404)
        data = json.loads(request.body)
        form = AddressForm(data, instance=address)
        if form.is_valid():
            updated_address = form.save(commit=False)
            if form.cleaned_data.get('is_default'):
                Address.objects.filter(customer=customer).exclude(id=address.id).update(is_default=False)
            updated_address.save()
            return JsonResponse({'success': True, 'message': 'Cập nhật địa chỉ thành công'})
        return JsonResponse({'success': False, 'error': 'Invalid data'}, status=400)

    if request.method == 'DELETE' and pk:
        try:
            address = Address.objects.get(id=pk, customer=customer)
        except Address.DoesNotExist:
            return JsonResponse({'error': 'Address not found'}, status=404)
        address.delete()
        return JsonResponse({'success': True, 'message': 'Xóa địa chỉ thành công'})

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def api_profile(request):
    customer = _get_or_create_customer(request.user)

    if request.method == 'GET':
        return JsonResponse(
            {
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'email': request.user.email,
                    'get_full_name': request.user.get_full_name(),
                },
                'customer': {
                    'phone': customer.phone,
                },
            }
        )

    if request.method in ['PUT', 'POST']:
        data = json.loads(request.body)
        user = request.user
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.email = data.get('email', user.email)
        user.save()
        customer.phone = data.get('phone', customer.phone)
        customer.save()
        return JsonResponse({'success': True, 'message': 'Lưu thông tin thành công'})

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def api_change_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not request.user.check_password(old_password):
            return JsonResponse({'success': False, 'error': 'Mật khẩu cũ không đúng'})

        request.user.set_password(new_password)
        request.user.save()
        return JsonResponse({'success': True, 'message': 'Cập nhật mật khẩu thành công'})

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def api_orders(request, pk=None):
    customer = _get_or_create_customer(request.user)

    if request.method == 'GET':
        if pk:
            try:
                order = Order.objects.get(id=pk, customer=customer)
            except Order.DoesNotExist:
                return JsonResponse({'error': 'Order not found'}, status=404)
            items = OrderItem.objects.filter(order=order)
            return JsonResponse(
                {
                    'order': {
                        'id': order.id,
                        'order_number': order.order_number,
                        'status': order.status,
                        'created_at': order.created_at.isoformat(),
                        'total_amount': order.total_amount,
                        'cancel_reason': order.cancel_reason,
                        'address': {
                            'full_name': order.address.full_name,
                            'phone': order.address.phone,
                            'email': order.address.email,
                            'province': order.address.province,
                            'district': order.address.district,
                            'ward': order.address.ward,
                            'address_detail': order.address.address_detail,
                        }
                        if order.address
                        else None,
                        'items': [
                            {
                                'product_name': item.product_name,
                                'quantity': item.quantity,
                                'unit_price': item.unit_price,
                            }
                            for item in items
                        ],
                    }
                }
            )

        orders = Order.objects.filter(customer=customer).select_related('address').order_by('-created_at')
        return JsonResponse(
            {
                'orders': [
                    {
                        'id': order.id,
                        'order_number': order.order_number,
                        'status': order.status,
                        'created_at': order.created_at.isoformat(),
                        'total_amount': order.total_amount,
                        'address': {
                            'full_name': order.address.full_name,
                            'phone': order.address.phone,
                            'email': order.address.email,
                            'province': order.address.province,
                            'district': order.address.district,
                            'ward': order.address.ward,
                            'address_detail': order.address.address_detail,
                        }
                        if order.address
                        else None,
                    }
                    for order in orders
                ]
            }
        )

    return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required
def api_cancel_order(request, pk):
    try:
        customer = Customer.objects.get(user=request.user)
        order = Order.objects.get(id=pk, customer=customer)
    except (Customer.DoesNotExist, Order.DoesNotExist):
        return JsonResponse({'error': 'Order not found'}, status=404)

    if request.method == 'POST':
        if order.status not in ['pending', 'processing']:
            return JsonResponse({'success': False, 'error': 'Không thể hủy đơn hàng ở trạng thái này'})

        data = json.loads(request.body)
        order.status = 'cancelled'
        order.cancel_reason = data.get('cancel_reason', '')
        order.save()
        return JsonResponse({'success': True, 'message': 'Hủy đơn hàng thành công'})

    return JsonResponse({'error': 'Method not allowed'}, status=405)
