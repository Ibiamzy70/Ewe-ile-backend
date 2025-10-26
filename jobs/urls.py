from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import JobViewSet, JobApplicationViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'applications', JobApplicationViewSet, basename='application')
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    path('', include(router.urls)),
]
