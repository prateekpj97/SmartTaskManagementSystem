import pytest
from django.contrib.auth.models import User
from tasks.models import Task, Category
from accounts.models import UserProfile
from datetime import datetime, timedelta
from django.utils import timezone


@pytest.fixture
def user(db):
    """Create a test user"""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    return user


@pytest.fixture
def another_user(db):
    """Create another test user"""
    user = User.objects.create_user(
        username='anotheruser',
        email='another@example.com',
        password='testpass123'
    )
    return user


@pytest.fixture
def category(db, user):
    """Create a test category"""
    return Category.objects.create(
        name='Work',
        description='Work related tasks',
        color='#007bff',
        user=user
    )


@pytest.fixture
def task(db, user, category):
    """Create a test task"""
    return Task.objects.create(
        title='Test Task',
        description='This is a test task',
        priority='medium',
        status='pending',
        category=category,
        user=user,
        deadline=timezone.now() + timedelta(days=7)
    )


@pytest.fixture
def completed_task(db, user, category):
    """Create a completed test task"""
    task = Task.objects.create(
        title='Completed Task',
        description='This task is completed',
        priority='high',
        status='completed',
        category=category,
        user=user,
        completed_at=timezone.now()
    )
    return task


@pytest.fixture
def overdue_task(db, user):
    """Create an overdue test task"""
    return Task.objects.create(
        title='Overdue Task',
        description='This task is overdue',
        priority='urgent',
        status='pending',
        user=user,
        deadline=timezone.now() - timedelta(days=2)
    )


@pytest.fixture
def api_client():
    """Create an API client"""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """Create an authenticated API client"""
    api_client.force_authenticate(user=user)
    return api_client

