from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task, Category


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'color', 'task_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_task_count(self, obj):
        return obj.tasks.count()


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model"""
    user = UserSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_until_deadline = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'priority', 'status', 
            'category', 'category_name', 'user', 'deadline', 
            'completed_at', 'reminder_sent', 'is_overdue', 
            'days_until_deadline', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'completed_at', 'reminder_sent', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        # Set the user from the request context
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for task lists"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'priority', 'status', 'category_name', 'deadline', 'created_at']

