from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import InstallationTask
from .forms import InstallationTaskForm
from apps.core.utils import get_paginated_data
from apps.core.decorators import staff_required
from django.contrib import messages


@login_required
@staff_required
def task_list(request):
    """View list of all assigned installation jobs for current staff"""
    tasks_query = InstallationTask.objects.filter(assigned_staff=request.user).order_by(
        "id"
    )

    completed_count = tasks_query.filter(status="completed").count()
    in_progress_count = tasks_query.filter(status="in_progress").count()

    # Use centralized pagination
    page_obj = get_paginated_data(tasks_query, request, 10)

    return render(
        request,
        "task_list.html",
        {
            "tasks": page_obj,  # Template expects 'tasks' name
            "page_obj": page_obj,
            "completed_count": completed_count,
            "in_progress_count": in_progress_count,
        },
    )


@login_required
@staff_required
def task_detail(request, pk):
    """View details of a specific installation task and update status using Django Form"""
    task = get_object_or_404(InstallationTask, pk=pk)

    if request.method == "POST":
        form = InstallationTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(
                request, f"Cập nhật trạng thái nhiệm vụ #{task.id} thành công."
            )
            return redirect("tasks:task_list")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = InstallationTaskForm(instance=task)

    return render(request, "task_detail.html", {"task": task, "form": form})
