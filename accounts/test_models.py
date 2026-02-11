import pytest
from django.contrib.auth.models import User
from accounts.models import UserProfile


@pytest.mark.django_db
class TestUserProfile:
    """Test UserProfile model"""
    
    def test_user_profile_created_on_user_creation(self):
        """Test that UserProfile is automatically created when User is created"""
        user = User.objects.create_user(
            username='newuser',
            email='newuser@example.com',
            password='password123'
        )
        assert hasattr(user, 'profile')
        assert isinstance(user.profile, UserProfile)
    
    def test_user_profile_str_method(self, user):
        """Test UserProfile string representation"""
        assert str(user.profile) == f"{user.username}'s profile"
    
    def test_user_profile_default_values(self, user):
        """Test UserProfile default values"""
        profile = user.profile
        assert profile.bio == ''
        assert profile.phone_number == ''
        assert profile.email_notifications is True
        assert profile.avatar.name == ''
    
    def test_user_profile_update(self, user):
        """Test updating UserProfile"""
        profile = user.profile
        profile.bio = 'Test bio'
        profile.phone_number = '1234567890'
        profile.email_notifications = False
        profile.save()
        
        profile.refresh_from_db()
        assert profile.bio == 'Test bio'
        assert profile.phone_number == '1234567890'
        assert profile.email_notifications is False

