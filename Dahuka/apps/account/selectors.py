from typing import Any, Optional
from django.db.models import QuerySet
from .models import Customer, Address

def get_customer_for_user(user: Any) -> Optional[Customer]:
    """Retrieves the customer profile for a given user."""
    if not user.is_authenticated:
        return None
    return Customer.objects.filter(user=user).first()

def get_addresses_for_customer(customer: Customer) -> QuerySet[Address]:
    """Retrieves all addresses for a customer, ordered by default and update time."""
    return Address.objects.filter(customer=customer).order_by('-is_default', '-updated_at')

def get_address_by_id(customer: Customer, address_id: int) -> Address:
    """Retrieves a specific address for a customer."""
    from django.shortcuts import get_object_or_404
    return get_object_or_404(Address, id=address_id, customer=customer)
