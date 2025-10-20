from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import ViewSets when they are created
# from .views import TicketViewSet, UserViewSet

router = DefaultRouter()
# router.register(r'tickets', TicketViewSet, basename='ticket')
# router.register(r'users', UserViewSet, basename='user')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),  # Browsable API login
]
