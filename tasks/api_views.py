from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import Task, Category
from .serializers import TaskSerializer, TaskListSerializer, CategorySerializer
from .tasks import send_task_notification


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category CRUD operations
    """
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        # Invalidate cache
        cache.delete(f'user_categories_{self.request.user.id}')


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task CRUD operations with caching
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'priority', 'category']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'deadline', 'priority']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return TaskSerializer
    
    def get_queryset(self):
        # Try to get from cache first
        cache_key = f'user_tasks_{self.request.user.id}'
        cached_tasks = cache.get(cache_key)
        
        if cached_tasks is None:
            queryset = Task.objects.filter(user=self.request.user).select_related('category', 'user')
            # Cache for 5 minutes
            cache.set(cache_key, list(queryset.values_list('id', flat=True)), 300)
        
        return Task.objects.filter(user=self.request.user).select_related('category', 'user')
    
    def perform_create(self, serializer):
        task = serializer.save(user=self.request.user)
        # Invalidate cache
        cache.delete(f'user_tasks_{self.request.user.id}')
        # Send notification asynchronously
        send_task_notification.delay(task.id, 'created')
    
    def perform_update(self, serializer):
        task = serializer.save()
        # Invalidate cache
        cache.delete(f'user_tasks_{self.request.user.id}')
        # Send notification asynchronously
        send_task_notification.delay(task.id, 'updated')
    
    def perform_destroy(self, instance):
        # Invalidate cache
        cache.delete(f'user_tasks_{self.request.user.id}')
        instance.delete()
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark a task as completed"""
        task = self.get_object()
        task.mark_as_completed()
        # Invalidate cache
        cache.delete(f'user_tasks_{request.user.id}')
        # Send notification
        send_task_notification.delay(task.id, 'completed')
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get task statistics for the current user"""
        cache_key = f'user_task_stats_{request.user.id}'
        stats = cache.get(cache_key)
        
        if stats is None:
            tasks = self.get_queryset()
            stats = {
                'total': tasks.count(),
                'pending': tasks.filter(status='pending').count(),
                'in_progress': tasks.filter(status='in_progress').count(),
                'completed': tasks.filter(status='completed').count(),
                'cancelled': tasks.filter(status='cancelled').count(),
                'overdue': tasks.filter(
                    deadline__lt=timezone.now(),
                    status__in=['pending', 'in_progress']
                ).count(),
                'high_priority': tasks.filter(priority='high').count(),
                'urgent_priority': tasks.filter(priority='urgent').count(),
            }
            # Cache for 2 minutes
            cache.set(cache_key, stats, 120)
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue tasks"""
        tasks = self.get_queryset().filter(
            deadline__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        )
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get tasks with upcoming deadlines (next 7 days)"""
        from datetime import timedelta
        now = timezone.now()
        next_week = now + timedelta(days=7)
        
        tasks = self.get_queryset().filter(
            deadline__gte=now,
            deadline__lte=next_week,
            status__in=['pending', 'in_progress']
        ).order_by('deadline')
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)

