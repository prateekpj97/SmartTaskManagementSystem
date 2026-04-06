from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.cache import cache
from django.http import JsonResponse
from django.db.models import Q, Count
from .models import Task, Category
from .forms import TaskForm, CategoryForm


@login_required
def dashboard(request):
    """Main dashboard view with task statistics"""
    cache_key = f'dashboard_stats_{request.user.id}'
    stats = cache.get(cache_key)

    if stats is None:
        now = timezone.now()
        # Optimized: Use single query with aggregation instead of multiple count() queries
        from django.db.models import Count, Q

        task_stats = Task.objects.filter(user=request.user).aggregate(
            total_tasks=Count('id'),
            pending_tasks=Count('id', filter=Q(status='pending')),
            in_progress_tasks=Count('id', filter=Q(status='in_progress')),
            completed_tasks=Count('id', filter=Q(status='completed')),
            overdue_tasks=Count('id', filter=Q(
                deadline__lt=now,
                status__in=['pending', 'in_progress']
            ))
        )

        stats = task_stats
        cache.set(cache_key, stats, 300)  # Increased cache time to 5 minutes

    # Optimized: Use select_related to prevent N+1 queries
    recent_tasks = Task.objects.filter(user=request.user)\
        .select_related('category')\
        .only('id', 'title', 'priority', 'created_at', 'category__name', 'category__color')\
        .order_by('-created_at')[:5]

    upcoming_tasks = Task.objects.filter(
        user=request.user,
        deadline__gte=timezone.now(),
        status__in=['pending', 'in_progress']
    ).select_related('category')\
     .only('id', 'title', 'priority', 'deadline', 'category__name', 'category__color')\
     .order_by('deadline')[:5]

    context = {
        'stats': stats,
        'recent_tasks': recent_tasks,
        'upcoming_tasks': upcoming_tasks,
    }
    return render(request, 'tasks/dashboard.html', context)


@login_required
def task_list(request):
    """List all tasks with filtering options"""
    # Optimized: Use select_related and only() to reduce query size
    tasks = Task.objects.filter(user=request.user)\
        .select_related('category')\
        .only(
            'id', 'title', 'priority', 'status', 'deadline',
            'category__id', 'category__name', 'category__color'
        )

    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    category_filter = request.GET.get('category')
    search_query = request.GET.get('search')

    # Build filters dynamically for better performance
    filters = Q()
    if status_filter:
        filters &= Q(status=status_filter)
    if priority_filter:
        filters &= Q(priority=priority_filter)
    if category_filter:
        filters &= Q(category_id=category_filter)
    if search_query:
        filters &= Q(title__icontains=search_query) | Q(description__icontains=search_query)

    if filters:
        tasks = tasks.filter(filters)

    # Order by deadline (overdue first), then priority
    tasks = tasks.order_by('deadline', '-priority')

    # Optimized: Only fetch necessary category fields
    categories = Category.objects.filter(user=request.user).only('id', 'name')

    context = {
        'tasks': tasks,
        'categories': categories,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'search_query': search_query,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_create(request):
    """Create a new task"""
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            cache.delete(f'user_tasks_{request.user.id}')
            cache.delete(f'dashboard_stats_{request.user.id}')
            messages.success(request, 'Task created successfully!')
            return redirect('task_list')
    else:
        form = TaskForm(user=request.user)

    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Create'})


@login_required
def task_update(request, pk):
    """Update an existing task"""
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            cache.delete(f'user_tasks_{request.user.id}')
            cache.delete(f'dashboard_stats_{request.user.id}')
            messages.success(request, 'Task updated successfully!')
            return redirect('task_list')
    else:
        form = TaskForm(instance=task, user=request.user)

    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Update', 'task': task})


@login_required
def task_delete(request, pk):
    """Delete a task"""
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        task.delete()
        cache.delete(f'user_tasks_{request.user.id}')
        cache.delete(f'dashboard_stats_{request.user.id}')
        messages.success(request, 'Task deleted successfully!')
        return redirect('task_list')

    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@login_required
def task_detail(request, pk):
    """View task details"""
    # Optimized: Use select_related to prevent additional query for category
    task = get_object_or_404(
        Task.objects.select_related('category', 'user'),
        pk=pk,
        user=request.user
    )
    return render(request, 'tasks/task_detail.html', {'task': task})


@login_required
def task_toggle_status(request, pk):
    """Toggle task status via AJAX"""
    if request.method == 'POST':
        task = get_object_or_404(Task, pk=pk, user=request.user)
        new_status = request.POST.get('status')

        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            if new_status == 'completed':
                task.mark_as_completed()
            else:
                task.save()

            cache.delete(f'user_tasks_{request.user.id}')
            cache.delete(f'dashboard_stats_{request.user.id}')

            return JsonResponse({
                'success': True,
                'status': task.get_status_display(),
                'completed_at': task.completed_at.isoformat() if task.completed_at else None
            })

    return JsonResponse({'success': False}, status=400)


@login_required
def category_list(request):
    """List all categories"""
    categories = Category.objects.filter(user=request.user).annotate(
        task_count=Count('tasks')
    )
    return render(request, 'tasks/category_list.html', {'categories': categories})


@login_required
def category_create(request):
    """Create a new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()

    return render(request, 'tasks/category_form.html', {'form': form, 'action': 'Create'})


@login_required
def category_update(request, pk):
    """Update a category"""
    category = get_object_or_404(Category, pk=pk, user=request.user)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'tasks/category_form.html', {'form': form, 'action': 'Update', 'category': category})


@login_required
def category_delete(request, pk):
    """Delete a category"""
    category = get_object_or_404(Category, pk=pk, user=request.user)

    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('category_list')

    return render(request, 'tasks/category_confirm_delete.html', {'category': category})
