from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import InstallationTask
from django.core.paginator import Paginator

def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def task_list(request):
    """View list of all assigned installation jobs for current staff"""
    tasks_list = InstallationTask.objects.all().order_by('-created_at')
    
    # Pagination
    paginator = Paginator(tasks_list, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'tasks/list.html', {'tasks': page_obj})

@login_required
@user_passes_test(is_staff)
def task_detail(request, pk):
    """View details of a specific installation task and update status"""
    task = get_object_or_404(InstallationTask, pk=pk)
    return render(request, 'tasks/detail.html', {'task': task})
