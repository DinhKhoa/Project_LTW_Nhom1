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

from apps.core.forms import (
    AddressForm,
    CancelOrderForm,
    CustomerForm,
    PasswordChangeForm,
)
from apps.orders.models import Order, OrderItem
from .models import Address, Customer
from .services import AccountService
from .forms import RegistrationForm, PublicPasswordChangeForm
from . import selectors
from .decorators import customer_required


def public_change_password(request: HttpRequest) -> HttpResponse:
    form = PublicPasswordChangeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        phone = form.cleaned_data["phone"]
        current_password = form.cleaned_data["current_password"]
        new_password = form.cleaned_data["new_password"]

        user = authenticate(request, username=phone, password=current_password)
        if user is not None:
            user.set_password(new_password)
            user.save()
            messages.success(
                request, "Đổi mật khẩu thành công. Vui lòng đăng nhập lại."
            )
            return redirect("login")
        else:
            messages.error(
                request, "Số điện thoại hoặc mật khẩu hiện tại không chính xác."
            )

    return render(request, "registration/password_reset_confirm.html", {"form": form})


@login_required
def account_dashboard(request: HttpRequest) -> HttpResponse:
    section = request.GET.get("section", "profile")

    if (request.user.is_staff or request.user.is_superuser) and section in [
        "orders",
        "addresses",
    ]:
        section = "profile"
        messages.warning(
            request, "Tài khoản nhân viên/admin không thể truy cập mục này."
        )

    section_map = {
        "orders": "account:purchase_list",
        "addresses": "account:address_list",
        "profile": "account:profile_view",
    }
    return redirect(section_map.get(section, "account:profile_view"))


@login_required
@customer_required
def address_list(request: HttpRequest) -> HttpResponse:
    customer = AccountService.get_or_create_customer(request.user)
    addresses = selectors.get_addresses_for_customer(customer)
    return render(
        request,
        "addresses.html",
        {
            "addresses": addresses,
            "customer": customer,
            "active_section": "addresses",
        },
    )


@login_required
@customer_required
def add_address(request: HttpRequest) -> HttpResponse:
    customer = AccountService.get_or_create_customer(request.user)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        if request.method == "POST":
            form = AddressForm(request.POST)
            if form.is_valid():
                AccountService.create_address(customer, form)
                return JsonResponse({"success": True})
            else:
                html = render_to_string(
                    "partials/_address_form.html",
                    {"form": form, "request": request, "submit_label": "Xác nhận"},
                    request=request,
                )
                return JsonResponse({"success": False, "html": html})
        else:
            form = AddressForm(initial={"address_type": "home"})
            html = render_to_string(
                "partials/_address_form.html",
                {"form": form, "request": request, "submit_label": "Xác nhận"},
                request=request,
            )
            return JsonResponse({"html": html})

    return redirect("account:address_list")


@login_required
@customer_required
def edit_address(request: HttpRequest, pk: int) -> HttpResponse:
    customer = AccountService.get_or_create_customer(request.user)
    address = selectors.get_address_by_id(customer, pk)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        if request.method == "POST":
            form = AddressForm(request.POST, instance=address)
            if form.is_valid():
                AccountService.update_address(customer, address, form)
                return JsonResponse({"success": True})
            else:
                html = render_to_string(
                    "partials/_address_form.html",
                    {"form": form, "request": request, "submit_label": "Cập nhật"},
                    request=request,
                )
                return JsonResponse({"success": False, "html": html})
        else:
            form = AddressForm(instance=address)
            html = render_to_string(
                "partials/_address_form.html",
                {"form": form, "request": request, "submit_label": "Cập nhật"},
                request=request,
            )
            return JsonResponse({"html": html})

    return redirect("account:address_list")


@login_required
@customer_required
def delete_address(request: HttpRequest, pk: int) -> HttpResponse:
    customer = AccountService.get_or_create_customer(request.user)
    address = selectors.get_address_by_id(customer, pk)

    if request.method == "POST":
        address.delete()
        messages.success(request, "Xóa địa chỉ thành công")
        return redirect("account:address_list")

    return redirect("account:address_list")


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    customer = AccountService.get_or_create_customer(request.user)

    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save(user=request.user)
            messages.success(request, "Lưu thông tin thành công")
            return redirect("account:profile_view")
    else:
        form = CustomerForm(
            initial={
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
                "phone": customer.phone,
            },
            instance=customer,
        )

    return render(
        request,
        "profile.html",
        {
            "form": form,
            "customer": customer,
            "active_section": "profile",
        },
    )


@login_required
def change_password(request: HttpRequest) -> HttpResponse:
    form = PasswordChangeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        success, message = AccountService.change_password(
            request,
            request.user,
            form.cleaned_data["old_password"],
            form.cleaned_data["new_password"],
        )
        if success:
            messages.success(request, message)
            return redirect("account:profile_view")
        messages.error(request, message)

    return render(
        request,
        "registration/password_change_form.html",
        {
            "form": form,
            "customer": AccountService.get_or_create_customer(request.user),
        },
    )


@login_required
@customer_required
def purchase_list(request: HttpRequest) -> HttpResponse:
    customer = AccountService.get_or_create_customer(request.user)

    query = request.GET.get("q", "")
    status = request.GET.get("status", "")

    orders_list = selectors.get_filtered_purchases(request.user, query, status)

    paginator = Paginator(orders_list, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    status_choices = Order.STATUS_CHOICES

    return render(
        request,
        "purchase_list.html",
        {
            "orders": page_obj,
            "customer": customer,
            "active_section": "orders",
            "status_choices": status_choices,
            "query": query,
            "current_status": status,
        },
    )


@login_required
def purchase_detail(request: HttpRequest, pk: int) -> HttpResponse:
    customer = AccountService.get_or_create_customer(request.user)
    items_qs = OrderItem.objects.select_related("product").all()

    if request.user.is_staff:
        order_filter = Q(id=pk)
    else:
        order_filter = Q(id=pk, customer=request.user)

    order = get_object_or_404(
        Order.objects.select_related("customer", "assigned_staff").prefetch_related(
            Prefetch("items", queryset=items_qs)
        ),
        order_filter,
    )
    view_type = "customer"
    staff_list = []
    if request.user.is_superuser:
        view_type = "admin"
        staff_list = User.objects.filter(is_staff=True)
    elif request.user.is_staff:
        view_type = "staff"

    return render(
        request,
        "purchase_detail.html",
        {
            "order": order,
            "items": order.items.all(),
            "customer": customer,
            "active_section": "orders",
            "view_type": view_type,
            "staff_list": staff_list,
            "cancel_form": CancelOrderForm(),
        },
    )


@login_required
@customer_required
def cancel_order(request: HttpRequest, pk: int) -> HttpResponse:
    customer = AccountService.get_or_create_customer(request.user)
    if request.user.is_staff:
        order_filter = Q(id=pk)
    else:
        order_filter = Q(id=pk, customer=request.user)

    order = get_object_or_404(Order, order_filter)

    if order.status not in ["pending", "processing"]:
        messages.error(request, "Không thể hủy đơn hàng ở trạng thái này")
        return redirect("account:purchase_detail", pk=pk)

    form = CancelOrderForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        success, message = AccountService.cancel_order(
            order, form.cleaned_data["cancel_reason"], user=request.user
        )
        if success:
            messages.success(request, message)
            return redirect("account:purchase_detail", pk=pk)
        messages.error(request, message)
        return redirect("account:purchase_detail", pk=pk)

    return render(
        request,
        "cancel_order.html",
        {
            "form": form,
            "order": order,
            "customer": customer,
            "active_section": "orders",
        },
    )


def signup(request: HttpRequest) -> HttpResponse:
    form = RegistrationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            AccountService.register_user(form.cleaned_data)

            messages.success(
                request, "Đăng ký tài khoản thành công. Vui lòng đăng nhập."
            )
            return redirect("login")
        except Exception as e:
            messages.error(request, f"Đã xảy ra lỗi: {str(e)}")

    return render(request, "registration/signup.html", {"form": form})
