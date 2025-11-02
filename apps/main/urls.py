from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('settings/', views.admin_settings, name='admin_settings'),
    path('debug-widget/', views.debug_widget_codes, name='debug_widget'),
]
