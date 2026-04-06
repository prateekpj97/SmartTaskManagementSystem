from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    """Category model for organizing tasks"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#007bff', help_text='Hex color code')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Task(models.Model):
    """Task model for managing user tasks - Optimized with better indexes"""

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks', db_index=True)
    deadline = models.DateTimeField(null=True, blank=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True, db_index=True)
    reminder_sent = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            # Composite indexes for common query patterns
            models.Index(fields=['user', 'status', 'deadline']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['user', 'priority', 'status']),
            models.Index(fields=['deadline', 'status', 'reminder_sent']),
            models.Index(fields=['status', 'completed_at']),
            # Text search optimization
            models.Index(fields=['title', 'user']),
        ]
        # Add database-level constraints for data integrity
        constraints = [
            models.CheckConstraint(
                check=Q(status__in=['pending', 'in_progress', 'completed', 'cancelled']),
                name='valid_status'
            ),
            models.CheckConstraint(
                check=Q(priority__in=['low', 'medium', 'high', 'urgent']),
                name='valid_priority'
            ),
        ]

    def __str__(self):
        return self.title

    def mark_as_completed(self):
        """Mark task as completed - Optimized to only update necessary fields"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        # Only update specific fields to reduce database load
        self.save(update_fields=['status', 'completed_at', 'updated_at'])

    @property
    def is_overdue(self):
        """Check if task is overdue - Using property for better performance"""
        if self.deadline and self.status not in ['completed', 'cancelled']:
            return timezone.now() > self.deadline
        return False

    @property
    def days_until_deadline(self):
        """Calculate days until deadline - Using property for consistency"""
        if self.deadline:
            delta = self.deadline - timezone.now()
            return delta.days
        return None

    @classmethod
    def get_active_tasks(cls, user):
        """Get all active tasks for a user - Optimized query method"""
        return cls.objects.filter(
            user=user,
            status__in=['pending', 'in_progress']
        ).select_related('category').order_by('deadline', '-priority')

    @classmethod
    def get_overdue_tasks(cls, user):
        """Get overdue tasks for a user - Optimized query method"""
        return cls.objects.filter(
            user=user,
            deadline__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        ).select_related('category').order_by('deadline')
