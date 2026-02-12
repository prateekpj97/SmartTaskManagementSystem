import pytest
from django.contrib.auth.models import User
from tasks.models import Task, Category
from django.utils import timezone
from datetime import timedelta


@pytest.mark.django_db
class TestCategoryModel:
    """Test Category model"""
    
    def test_category_creation(self, user):
        """Test creating a category"""
        category = Category.objects.create(
            name='Personal',
            description='Personal tasks',
            color='#ff0000',
            user=user
        )
        assert category.name == 'Personal'
        assert category.user == user
        assert str(category) == 'Personal'
    
    def test_category_str_method(self, category):
        """Test category string representation"""
        assert str(category) == category.name


@pytest.mark.django_db
class TestTaskModel:
    """Test Task model"""
    
    def test_task_creation(self, user, category):
        """Test creating a task"""
        task = Task.objects.create(
            title='New Task',
            description='Task description',
            priority='high',
            status='pending',
            category=category,
            user=user
        )
        assert task.title == 'New Task'
        assert task.user == user
        assert task.category == category
        assert str(task) == 'New Task'
    
    def test_task_str_method(self, task):
        """Test task string representation"""
        assert str(task) == task.title
    
    def test_mark_as_completed(self, task):
        """Test marking task as completed"""
        assert task.status != 'completed'
        assert task.completed_at is None
        
        task.mark_as_completed()
        
        assert task.status == 'completed'
        assert task.completed_at is not None
    
    def test_is_overdue_true(self, overdue_task):
        """Test is_overdue returns True for overdue tasks"""
        assert overdue_task.is_overdue() is True
    
    def test_is_overdue_false(self, task):
        """Test is_overdue returns False for future tasks"""
        assert task.is_overdue() is False
    
    def test_is_overdue_completed_task(self, completed_task):
        """Test is_overdue returns False for completed tasks"""
        assert completed_task.is_overdue() is False
    
    def test_days_until_deadline(self, task):
        """Test days_until_deadline calculation"""
        days = task.days_until_deadline()
        assert days is not None
        assert days >= 6 
    
    def test_days_until_deadline_no_deadline(self, user):
        """Test days_until_deadline with no deadline"""
        task = Task.objects.create(
            title='No Deadline Task',
            user=user,
            priority='low',
            status='pending'
        )
        assert task.days_until_deadline() is None
    
    def test_task_priority_choices(self, task):
        """Test task priority choices"""
        priorities = ['low', 'medium', 'high', 'urgent']
        for priority in priorities:
            task.priority = priority
            task.save()
            assert task.priority == priority
    
    def test_task_status_choices(self, task):
        """Test task status choices"""
        statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        for status in statuses:
            task.status = status
            task.save()
            assert task.status == status
    
    def test_task_without_category(self, user):
        """Test creating task without category"""
        task = Task.objects.create(
            title='No Category Task',
            user=user,
            priority='medium',
            status='pending'
        )
        assert task.category is None
    
    def test_task_ordering(self, user):
        """Test tasks are ordered by created_at descending"""
        task1 = Task.objects.create(title='Task 1', user=user, priority='low', status='pending')
        task2 = Task.objects.create(title='Task 2', user=user, priority='low', status='pending')
        
        tasks = Task.objects.all()
        assert tasks[0] == task2
        assert tasks[1] == task1

