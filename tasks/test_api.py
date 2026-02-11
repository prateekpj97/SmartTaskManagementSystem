import pytest
from django.urls import reverse
from rest_framework import status
from tasks.models import Task, Category


@pytest.mark.django_db
class TestTaskAPI:
    """Test Task API endpoints"""
    
    def test_list_tasks_unauthenticated(self, api_client):
        """Test listing tasks without authentication"""
        url = reverse('api-task-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    def test_list_tasks_authenticated(self, authenticated_client, task):
        """Test listing tasks with authentication"""
        url = reverse('api-task-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
    
    def test_create_task(self, authenticated_client, category):
        """Test creating a task via API"""
        url = reverse('api-task-list')
        data = {
            'title': 'API Created Task',
            'description': 'Created via API',
            'priority': 'high',
            'status': 'pending',
            'category': category.id
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Task.objects.filter(title='API Created Task').exists()
    
    def test_retrieve_task(self, authenticated_client, task):
        """Test retrieving a single task"""
        url = reverse('api-task-detail', kwargs={'pk': task.id})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == task.title
    
    def test_update_task(self, authenticated_client, task):
        """Test updating a task via API"""
        url = reverse('api-task-detail', kwargs={'pk': task.id})
        data = {
            'title': 'Updated via API',
            'description': task.description,
            'priority': 'urgent',
            'status': 'in_progress'
        }
        response = authenticated_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.title == 'Updated via API'
    
    def test_delete_task(self, authenticated_client, task):
        """Test deleting a task via API"""
        url = reverse('api-task-detail', kwargs={'pk': task.id})
        task_id = task.id
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Task.objects.filter(id=task_id).exists()
    
    def test_mark_task_completed(self, authenticated_client, task):
        """Test marking task as completed via API"""
        url = reverse('api-task-mark-completed', kwargs={'pk': task.id})
        response = authenticated_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        task.refresh_from_db()
        assert task.status == 'completed'
        assert task.completed_at is not None
    
    def test_task_statistics(self, authenticated_client, task):
        """Test task statistics endpoint"""
        url = reverse('api-task-statistics')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'total' in response.data
        assert 'pending' in response.data
        assert 'completed' in response.data
    
    def test_overdue_tasks(self, authenticated_client, overdue_task):
        """Test overdue tasks endpoint"""
        url = reverse('api-task-overdue')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
    
    def test_upcoming_tasks(self, authenticated_client, task):
        """Test upcoming tasks endpoint"""
        url = reverse('api-task-upcoming')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestCategoryAPI:
    """Test Category API endpoints"""
    
    def test_list_categories(self, authenticated_client, category):
        """Test listing categories"""
        url = reverse('api-category-list')
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1
    
    def test_create_category(self, authenticated_client):
        """Test creating a category via API"""
        url = reverse('api-category-list')
        data = {
            'name': 'API Category',
            'description': 'Created via API',
            'color': '#ff00ff'
        }
        response = authenticated_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Category.objects.filter(name='API Category').exists()
    
    def test_retrieve_category(self, authenticated_client, category):
        """Test retrieving a single category"""
        url = reverse('api-category-detail', kwargs={'pk': category.id})
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == category.name
    
    def test_update_category(self, authenticated_client, category):
        """Test updating a category via API"""
        url = reverse('api-category-detail', kwargs={'pk': category.id})
        data = {
            'name': 'Updated Category',
            'description': 'Updated description',
            'color': '#00ff00'
        }
        response = authenticated_client.put(url, data)
        assert response.status_code == status.HTTP_200_OK
        category.refresh_from_db()
        assert category.name == 'Updated Category'
    
    def test_delete_category(self, authenticated_client, category):
        """Test deleting a category via API"""
        url = reverse('api-category-detail', kwargs={'pk': category.id})
        category_id = category.id
        response = authenticated_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Category.objects.filter(id=category_id).exists()
    
    def test_filter_tasks_by_category(self, authenticated_client, task, category):
        """Test filtering tasks by category"""
        url = reverse('api-task-list') + f'?category={category.id}'
        response = authenticated_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        for task_data in response.data['results']:
            assert task_data['category'] == category.id

