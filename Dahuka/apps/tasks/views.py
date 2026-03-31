from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def danh_sach_nhiem_vu(request):
    """View list of all assigned installation jobs for current staff"""
    return render(request, 'tasks/congvieclapdat.html')

@login_required
@user_passes_test(is_staff)
def chi_tiet_nhiem_vu(request):
    """View details of a specific installation task and update status"""
    return render(request, 'tasks/chitietlapdat.html')
