from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'email_notifications', 'created_at']
    list_filter = ['email_notifications', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number']
    ordering = ['-created_at']
