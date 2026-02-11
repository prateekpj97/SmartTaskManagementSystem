import pytest
from django.urls import reverse
from django.contrib.auth.models import User


@pytest.mark.django_db
class TestRegistrationView:
    """Test user registration view"""
    
    def test_registration_get(self, client):
        """Test GET request to registration page"""
        response = client.get(reverse('register'))
        assert response.status_code == 200
        assert 'form' in response.context
    
    def test_registration_post_success(self, client):
        """Test successful user registration"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        response = client.post(reverse('register'), data)
        assert response.status_code == 302  # Redirect to login
        assert User.objects.filter(username='newuser').exists()
    
    def test_registration_password_mismatch(self, client):
        """Test registration with mismatched passwords"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password_confirm': 'differentpass'
        }
        response = client.post(reverse('register'), data)
        assert response.status_code == 200
        assert not User.objects.filter(username='newuser').exists()
    
    def test_registration_duplicate_email(self, client, user):
        """Test registration with duplicate email"""
        data = {
            'username': 'newuser',
            'email': user.email,
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        response = client.post(reverse('register'), data)
        assert response.status_code == 200
        assert not User.objects.filter(username='newuser').exists()


@pytest.mark.django_db
class TestLoginView:
    """Test user login view"""
    
    def test_login_get(self, client):
        """Test GET request to login page"""
        response = client.get(reverse('login'))
        assert response.status_code == 200
        assert 'form' in response.context
    
    def test_login_post_success(self, client, user):
        """Test successful login"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = client.post(reverse('login'), data)
        assert response.status_code == 302  # Redirect to dashboard
    
    def test_login_post_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        data = {
            'username': 'wronguser',
            'password': 'wrongpass'
        }
        response = client.post(reverse('login'), data)
        assert response.status_code == 200
        assert not response.wsgi_request.user.is_authenticated
    
    def test_login_redirect_authenticated_user(self, client, user):
        """Test that authenticated users are redirected from login page"""
        client.force_login(user)
        response = client.get(reverse('login'))
        assert response.status_code == 302


@pytest.mark.django_db
class TestLogoutView:
    """Test user logout view"""
    
    def test_logout(self, client, user):
        """Test user logout"""
        client.force_login(user)
        response = client.get(reverse('logout'))
        assert response.status_code == 302  # Redirect to login
        
        # Check that user is logged out
        response = client.get(reverse('dashboard'))
        assert response.status_code == 302  # Should redirect to login


@pytest.mark.django_db
class TestProfileView:
    """Test user profile view"""
    
    def test_profile_requires_login(self, client):
        """Test profile page requires authentication"""
        response = client.get(reverse('profile'))
        assert response.status_code == 302
    
    def test_profile_get(self, client, user):
        """Test GET request to profile page"""
        client.force_login(user)
        response = client.get(reverse('profile'))
        assert response.status_code == 200
        assert 'form' in response.context
    
    def test_profile_update(self, client, user):
        """Test updating user profile"""
        client.force_login(user)
        data = {
            'bio': 'Updated bio',
            'phone_number': '9876543210',
            'email_notifications': False
        }
        response = client.post(reverse('profile'), data)
        assert response.status_code == 302
        
        user.profile.refresh_from_db()
        assert user.profile.bio == 'Updated bio'
        assert user.profile.phone_number == '9876543210'
        assert user.profile.email_notifications is False

