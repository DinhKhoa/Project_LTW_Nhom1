from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Customer, Address
from apps.orders.models import Order

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def api_profile(request):
    customer = get_object_or_404(Customer, user=request.user)
    if request.method == 'GET':
        return Response({
            'username': request.user.username,
            'full_name': request.user.get_full_name(),
            'phone': customer.phone,
            'points': customer.points
        })
    # Handle POST if needed
    return Response({'status': 'Profile updated'})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_change_password(request):
    # Simplified logic
    return Response({'status': 'Password change request received'})

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def api_addresses(request, pk=None):
    customer = get_object_or_404(Customer, user=request.user)
    if request.method == 'GET':
        if pk:
            addr = get_object_or_404(Address, pk=pk, customer=customer)
            return Response({'address': addr.address_detail})
        addrs = Address.objects.filter(customer=customer)
        return Response({'count': addrs.count()})
    return Response({'status': 'Success'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_orders(request, pk=None):
    customer = get_object_or_404(Customer, user=request.user)
    if pk:
        order = get_object_or_404(Order, pk=pk, customer=request.user)
        return Response({'id': order.id, 'total': order.total_amount})
    orders = Order.objects.filter(customer=request.user)
    return Response({'count': orders.count()})
