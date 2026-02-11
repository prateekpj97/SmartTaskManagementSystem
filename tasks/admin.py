from django.contrib import admin
from .models import Task, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'description']
    ordering = ['name']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'priority', 'status', 'category', 'deadline', 'created_at']
    list_filter = ['status', 'priority', 'category', 'created_at', 'deadline']
    search_fields = ['title', 'description']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'user')
        }),
        ('Task Details', {
            'fields': ('priority', 'status', 'category', 'deadline')
        }),
        ('Metadata', {
            'fields': ('completed_at', 'reminder_sent', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at', 'completed_at']
