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
    """Task model for managing user tasks"""

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

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    deadline = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['deadline']),
            models.Index(fields=['priority']),
        ]

    def __str__(self):
        return self.title

    def mark_as_completed(self):
        """Mark task as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

    def is_overdue(self):
        """Check if task is overdue"""
        if self.deadline and self.status != 'completed':
            return timezone.now() > self.deadline
        return False

    def days_until_deadline(self):
        """Calculate days until deadline"""
        if self.deadline:
            delta = self.deadline - timezone.now()
            return delta.days
        return None
