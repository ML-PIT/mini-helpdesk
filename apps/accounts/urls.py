from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import user_management_views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile_edit, name='profile_edit'),
    path('change_password/', views.change_password, name='change_password'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),

    # Microsoft OAuth2 URLs (to be implemented)
    # path('microsoft/', views.microsoft_login, name='microsoft_login'),
    # path('microsoft/callback/', views.microsoft_callback, name='microsoft_callback'),
    
    # User Management URLs
    path('users/', user_management_views.user_list, name='user_list'),
    path('users/create/', user_management_views.user_create, name='user_create'),
    path('users/<int:user_id>/', user_management_views.user_detail, name='user_detail'),
    path('users/<int:user_id>/edit/', user_management_views.user_edit, name='user_edit'),
    path('users/<int:user_id>/toggle-status/', user_management_views.user_toggle_status, name='user_toggle_status'),
    path('users/<int:user_id>/reset-password/', user_management_views.user_reset_password, name='user_reset_password'),
]
