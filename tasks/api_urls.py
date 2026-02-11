from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import TaskViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='api-task')
router.register(r'categories', CategoryViewSet, basename='api-category')

urlpatterns = [
    path('', include(router.urls)),
]

