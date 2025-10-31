"""
REST API URL Configuration for ABoro-Soft Helpdesk
Provides complete API endpoints for Desktop clients and third-party integrations
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'tickets', views.TicketViewSet, basename='ticket')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'stats', views.StatsViewSet, basename='stats')
router.register(r'health', views.HealthCheckViewSet, basename='health')

app_name = 'api'

urlpatterns = [
    # API v1 routes with router
    path('v1/', include(router.urls)),

    # API Authentication endpoints
    path('v1/auth/login/', views.AuthViewSet.as_view({'post': 'login'}), name='login'),
    path('v1/auth/logout/', views.AuthViewSet.as_view({'post': 'logout'}), name='logout'),
    path('v1/auth/validate-license/', views.AuthViewSet.as_view({'post': 'validate_license'}), name='validate_license'),

    # DRF Browsable API authentication
    path('auth/', include('rest_framework.urls')),
]
