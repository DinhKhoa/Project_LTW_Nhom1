from typing import Any, Dict, Optional
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Prefetch, Q

from apps.core.forms import AddressForm, CancelOrderForm, CustomerForm, PasswordChangeForm
from apps.orders.models import Order, OrderItem
from .models import Address, Customer
from .services import AccountService
from .forms import RegistrationForm, PublicPasswordChangeForm
from . import selectors
from .decorators import customer_required


def public_change_password(request: HttpRequest) -> HttpResponse:
    """
    Public view to change password via phone number verification.
    """
    form = PublicPasswordChangeForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        phone = form.cleaned_data['phone']
        current_password = form.cleaned_data['current_password']
        new_password = form.cleaned_data['new_password']
        
        user = authenticate(request, username=phone, password=current_password)
        if user is not None:
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Đổi mật khẩu thành công. Vui lòng đăng nhập lại.')
            return redirect('login')
        else:
            messages.error(request, 'Số điện thoại hoặc mật khẩu hiện tại không chính xác.')

    return render(request, 'public_change_password.html', {'form': form})


@login_required
def account_dashboard(request: HttpRequest) -> HttpResponse:
    """
    Redirects to the appropriate section of the account dashboard.
    """
    section = request.GET.get('section', 'profile')
    
    # If staff/admin tries to access restricted sections via dashboard URL
    if (request.user.is_staff or request.user.is_superuser) and section in ['orders', 'addresses']:
        section = 'profile'
        messages.warning(request, "Tài khoản nhân viên/admin không thể truy cập mục này.")

    section_map = {
        'orders': 'purchase_list',
        'addresses': 'address_list',
        'profile': 'profile_view',
    }
    return redirect(section_map.get(section, 'profile_view'))


@login_required
@customer_required
def address_list(request: HttpRequest) -> HttpResponse:
    """
    Displays a list of customer addresses.
    """
    customer = AccountService.get_or_create_customer(request.user)
    addresses = selectors.get_addresses_for_customer(customer)
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
@customer_required
def add_address(request: HttpRequest) -> HttpResponse:
    """
    Handles adding a new address for the customer.
    """
    customer = AccountService.get_or_create_customer(request.user)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.method == 'POST':
            form = AddressForm(request.POST)
            if form.is_valid():
                AccountService.create_address(customer, form)
                return JsonResponse({'success': True})
            else:
                html = render_to_string('partials/_address_form.html', {
                    'form': form, 
                    'request': request,
                    'submit_label': 'Xác nhận'
                }, request=request)
                return JsonResponse({'success': False, 'html': html})
        else:
            form = AddressForm(initial={'address_type': 'home'})
            html = render_to_string('partials/_address_form.html', {
                'form': form, 
                'request': request,
                'submit_label': 'Xác nhận'
            }, request=request)
            return JsonResponse({'html': html})

    return redirect('address_list')


@login_required
@customer_required
def edit_address(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Handles editing an existing address.
    """
    customer = AccountService.get_or_create_customer(request.user)
    address = selectors.get_address_by_id(customer, pk)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.method == 'POST':
            form = AddressForm(request.POST, instance=address)
            if form.is_valid():
                AccountService.update_address(customer, address, form)
                return JsonResponse({'success': True})
            else:
                html = render_to_string('partials/_address_form.html', {
                    'form': form, 
                    'request': request,
                    'submit_label': 'Cập nhật'
                }, request=request)
                return JsonResponse({'success': False, 'html': html})
        else:
            form = AddressForm(instance=address)
            html = render_to_string('partials/_address_form.html', {
                'form': form, 
                'request': request,
                'submit_label': 'Cập nhật'
            }, request=request)
            return JsonResponse({'html': html})

    return redirect('address_list')


@login_required
@customer_required
def delete_address(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Handles address deletion.
    """
    customer = AccountService.get_or_create_customer(request.user)
    address = selectors.get_address_by_id(customer, pk)

    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Xóa địa chỉ thành công')
        return redirect('address_list')

    return redirect('address_list')


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    """
    Displays and handles updates to the user profile.
    """
    customer = AccountService.get_or_create_customer(request.user)

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
def change_password(request: HttpRequest) -> HttpResponse:
    """
    Handles password changes for authenticated users.
    """
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
            'customer': AccountService.get_or_create_customer(request.user),
        },
    )


@login_required
@customer_required
def purchase_list(request: HttpRequest) -> HttpResponse:
    """
    Lists purchases for the current user with search and status filtering.
    """
    customer = AccountService.get_or_create_customer(request.user)
    
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')
    
    orders_list = Order.objects.filter(customer=request.user).select_related('customer', 'assigned_staff')
    
    if query:
        # Search by ID, recipient name, phone, or product name/SKU
        search_filter = Q(full_name__icontains=query) | Q(phone__icontains=query) | \
                        Q(items__product__name__icontains=query) | Q(items__product__sku__icontains=query)
        if query.isdigit():
            search_filter |= Q(id=query)
        orders_list = orders_list.filter(search_filter).distinct()
        
    if status:
        orders_list = orders_list.filter(status=status)
        
    orders_list = orders_list.order_by('-created_at')
    
    paginator = Paginator(orders_list, 5) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Status choices for filtering
    status_choices = Order.STATUS_CHOICES

    return render(
        request,
        'purchase_list.html',
        {
            'orders': page_obj,
            'customer': customer,
            'active_section': 'orders',
            'status_choices': status_choices,
            'query': query,
            'current_status': status,
        },
    )


@login_required
def purchase_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Displays details for a specific purchase.
    """
    customer = AccountService.get_or_create_customer(request.user)
    items_qs = OrderItem.objects.select_related('product').all()
    
    # Allow staff to view any order, but customers only their own
    if request.user.is_staff:
        order_filter = Q(id=pk)
    else:
        order_filter = Q(id=pk, customer=request.user)

    order = get_object_or_404(
        Order.objects.select_related('customer', 'assigned_staff').prefetch_related(
            Prefetch('items', queryset=items_qs)
        ),
        order_filter
    )
    # Determine view_type for template logic
    view_type = 'customer'
    staff_list = []
    if request.user.is_superuser:
        view_type = 'admin'
        staff_list = User.objects.filter(is_staff=True)
    elif request.user.is_staff:
        view_type = 'staff'

    return render(
        request,
        'purchase_detail.html',
        {
            'order': order,
            'items': order.items.all(),
            'customer': customer,
            'active_section': 'orders',
            'view_type': view_type,
            'staff_list': staff_list,
            'cancel_form': CancelOrderForm(),
        },
    )


@login_required
@customer_required
def cancel_order(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Handles order cancellation request.
    """
    customer = AccountService.get_or_create_customer(request.user)
    # Allow staff to cancel any order, but customers only their own
    if request.user.is_staff:
        order_filter = Q(id=pk)
    else:
        order_filter = Q(id=pk, customer=request.user)
        
    order = get_object_or_404(Order, order_filter)

    if order.status not in ['pending', 'processing']:
        messages.error(request, 'Không thể hủy đơn hàng ở trạng thái này')
        return redirect('purchase_detail', pk=pk)

    form = CancelOrderForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        success, message = AccountService.cancel_order(order, form.cleaned_data['cancel_reason'], user=request.user)
        if success:
            messages.success(request, message)
            return redirect('purchase_detail', pk=pk)
        messages.error(request, message)
        return redirect('purchase_detail', pk=pk)

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


def signin(request: HttpRequest) -> HttpResponse:
    """
    Handles new user registration.
    """
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
            
            if birthday:
                customer = user.customer
                customer.birthday = birthday
                customer.save()

            messages.success(request, 'Đăng ký tài khoản thành công. Vui lòng đăng nhập.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Đã xảy ra lỗi: {str(e)}')

    return render(request, 'registration/signup.html', {'form': form})
