from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),
    path('register/', views.register, name='register'),
    path('change_password/', views.change_password, name='change_password'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),

    # Microsoft OAuth2 URLs (to be implemented)
    # path('microsoft/', views.microsoft_login, name='microsoft_login'),
    # path('microsoft/callback/', views.microsoft_callback, name='microsoft_callback'),
]
