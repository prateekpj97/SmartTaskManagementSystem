import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from tasks.models import Task, Category


@pytest.mark.django_db
class TestDashboardView:
    """Test dashboard view"""
    
    def test_dashboard_requires_login(self, client):
        """Test dashboard requires authentication"""
        response = client.get(reverse('dashboard'))
        assert response.status_code == 302
    
    def test_dashboard_authenticated(self, client, user):
        """Test dashboard with authenticated user"""
        client.force_login(user)
        response = client.get(reverse('dashboard'))
        assert response.status_code == 200
        assert 'stats' in response.context
    
    def test_dashboard_shows_statistics(self, client, user, task):
        """Test dashboard shows correct statistics"""
        client.force_login(user)
        response = client.get(reverse('dashboard'))
        
        assert response.context['stats']['total_tasks'] >= 1
        assert 'recent_tasks' in response.context
        assert 'upcoming_tasks' in response.context


@pytest.mark.django_db
class TestTaskListView:
    """Test task list view"""
    
    def test_task_list_requires_login(self, client):
        """Test task list requires authentication"""
        response = client.get(reverse('task_list'))
        assert response.status_code == 302
    
    def test_task_list_authenticated(self, client, user, task):
        """Test task list with authenticated user"""
        client.force_login(user)
        response = client.get(reverse('task_list'))
        assert response.status_code == 200
        assert task in response.context['tasks']
    
    def test_task_list_filtering_by_status(self, client, user, task):
        """Test filtering tasks by status"""
        client.force_login(user)
        response = client.get(reverse('task_list') + '?status=pending')
        assert response.status_code == 200
        assert all(t.status == 'pending' for t in response.context['tasks'])
    
    def test_task_list_search(self, client, user, task):
        """Test searching tasks"""
        client.force_login(user)
        response = client.get(reverse('task_list') + f'?search={task.title}')
        assert response.status_code == 200
        assert task in response.context['tasks']


@pytest.mark.django_db
class TestTaskCreateView:
    """Test task create view"""
    
    def test_task_create_get(self, client, user):
        """Test GET request to create task"""
        client.force_login(user)
        response = client.get(reverse('task_create'))
        assert response.status_code == 200
        assert 'form' in response.context
    
    def test_task_create_post(self, client, user, category):
        """Test POST request to create task"""
        client.force_login(user)
        data = {
            'title': 'New Test Task',
            'description': 'Description',
            'priority': 'high',
            'status': 'pending',
            'category': category.id,
        }
        response = client.post(reverse('task_create'), data)
        assert response.status_code == 302
        assert Task.objects.filter(title='New Test Task').exists()


@pytest.mark.django_db
class TestTaskUpdateView:
    """Test task update view"""
    
    def test_task_update_get(self, client, user, task):
        """Test GET request to update task"""
        client.force_login(user)
        response = client.get(reverse('task_update', kwargs={'pk': task.id}))
        assert response.status_code == 200
        assert response.context['form'].instance == task
    
    def test_task_update_post(self, client, user, task):
        """Test POST request to update task"""
        client.force_login(user)
        data = {
            'title': 'Updated Task Title',
            'description': task.description,
            'priority': 'urgent',
            'status': 'in_progress',
        }
        response = client.post(reverse('task_update', kwargs={'pk': task.id}), data)
        task.refresh_from_db()
        assert task.title == 'Updated Task Title'
        assert task.priority == 'urgent'
    
    def test_task_update_other_user_task(self, client, user, another_user):
        """Test user cannot update another user's task"""
        other_task = Task.objects.create(
            title='Other User Task',
            user=another_user,
            priority='low',
            status='pending'
        )
        client.force_login(user)
        response = client.get(reverse('task_update', kwargs={'pk': other_task.id}))
        assert response.status_code == 404


@pytest.mark.django_db
class TestTaskDeleteView:
    """Test task delete view"""
    
    def test_task_delete_get(self, client, user, task):
        """Test GET request to delete task"""
        client.force_login(user)
        response = client.get(reverse('task_delete', kwargs={'pk': task.id}))
        assert response.status_code == 200
    
    def test_task_delete_post(self, client, user, task):
        """Test POST request to delete task"""
        client.force_login(user)
        task_id = task.id
        response = client.post(reverse('task_delete', kwargs={'pk': task_id}))
        assert response.status_code == 302
        assert not Task.objects.filter(id=task_id).exists()


@pytest.mark.django_db
class TestCategoryViews:
    """Test category views"""
    
    def test_category_list(self, client, user, category):
        """Test category list view"""
        client.force_login(user)
        response = client.get(reverse('category_list'))
        assert response.status_code == 200
        assert category in response.context['categories']
    
    def test_category_create(self, client, user):
        """Test category create view"""
        client.force_login(user)
        data = {
            'name': 'New Category',
            'description': 'Description',
            'color': '#00ff00'
        }
        response = client.post(reverse('category_create'), data)
        assert response.status_code == 302
        assert Category.objects.filter(name='New Category').exists()

