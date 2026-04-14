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
    # Lọc công việc theo nhân viên hiện tại để khớp với template
    tasks_query = InstallationTask.objects.filter(staff_name=request.user.get_full_name() or request.user.username).order_by('-created_at')
    
    completed_count = tasks_query.filter(status='completed').count()
    in_progress_count = tasks_query.filter(status='in_progress').count()
    
    # Pagination
    paginator = Paginator(tasks_query, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'tasks/list.html', {
        'tasks': page_obj,
        'completed_count': completed_count,
        'in_progress_count': in_progress_count
    })

@login_required
@user_passes_test(is_staff)
def task_detail(request, pk):
    """View details of a specific installation task and update status"""
    task = get_object_or_404(InstallationTask, pk=pk)
    return render(request, 'tasks/detail.html', {'task': task})
