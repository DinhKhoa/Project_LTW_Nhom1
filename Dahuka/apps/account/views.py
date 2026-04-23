import json
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.core.forms import AddressForm, CancelOrderForm, CustomerForm, PasswordChangeForm
from .models import Address, Customer
from apps.orders.models import Order, OrderItem
from .services import AccountService
from .forms import RegistrationForm

def _get_or_create_customer(user):
    return AccountService.get_or_create_customer(user)

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
        'addresses.html',
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
            AccountService.create_address(customer, form)
            messages.success(request, 'Thêm địa chỉ thành công')
            return redirect('address_list')
    else:
        form = AddressForm(initial={'address_type': 'home'})

    return render(
        request,
        'address_form.html',
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
            AccountService.update_address(customer, address, form)
            messages.success(request, 'Cập nhật địa chỉ thành công')
            return redirect('address_list')
    else:
        form = AddressForm(instance=address)

    return render(
        request,
        'address_form.html',
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
        'delete_address.html',
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
        'profile.html',
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
        success, message = AccountService.change_password(
            request,
            request.user, 
            form.cleaned_data['old_password'], 
            form.cleaned_data['new_password']
        )
        if success:
            messages.success(request, message)
            return redirect('profile_view')
        messages.error(request, message)

    return render(
        request,
        'change_password.html',
        {
            'form': form,
            'customer': _get_or_create_customer(request.user),
        },
    )

from django.core.paginator import Paginator

@login_required
def order_list(request):
    customer = _get_or_create_customer(request.user)
    # Use select_related to avoid N+1 queries when accessing order.customer
    orders_list = Order.objects.filter(customer=request.user).select_related('customer', 'assigned_staff').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(orders_list, 5) # 5 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(
        request,
        'orders.html',
        {
            'orders': page_obj,
            'customer': customer,
            'active_section': 'orders',
        },
    )

@login_required
def order_detail(request, pk):
    from django.db.models import Prefetch
    
    customer = _get_or_create_customer(request.user)
    # Use prefetch_related to load items and their products in one query
    items_qs = OrderItem.objects.select_related('product').all()
    order = get_object_or_404(
        Order.objects.select_related('customer', 'assigned_staff').prefetch_related(
            Prefetch('items', queryset=items_qs)
        ),
        id=pk,
        customer=request.user
    )
    items = order.items.all()  # Already prefetched
    return render(
        request,
        'order_detail.html',
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
    order = get_object_or_404(Order, id=pk, customer=request.user)

    if order.status not in ['pending', 'processing']:
        messages.error(request, 'Không thể hủy đơn hàng ở trạng thái này')
        return redirect('order_detail', pk=pk)

    form = CancelOrderForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        success, message = AccountService.cancel_order(order, form.cleaned_data['cancel_reason'])
        if success:
            messages.success(request, message)
            return redirect('order_detail', pk=pk)
        messages.error(request, message)
        return redirect('order_detail', pk=pk)

    return render(
        request,
        'cancel_order.html',
        {
            'form': form,
            'order': order,
            'customer': customer,
            'active_section': 'orders',
        },
    )




from django.contrib.auth.models import User
def signin(request):
    form = RegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        try:
            last_name = form.cleaned_data['last_name']
            first_name = form.cleaned_data['first_name']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data['email']
            birthday = form.cleaned_data['birthday']
            password = form.cleaned_data['password']

            user = User.objects.create_user(
                username=phone,
                password=password,
                email=email if email else '',
                first_name=first_name,
                last_name=last_name
            )
            
            # Customer creation is now handled by Signals! 
            # But we update birthday since it's not in User model
            if birthday:
                customer = user.customer
                customer.birthday = birthday
                customer.save()

            messages.success(request, 'Đăng ký tài khoản thành công. Vui lòng đăng nhập.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Đã xảy ra lỗi: {str(e)}')

    return render(request, 'registration/signup.html', {'form': form})
