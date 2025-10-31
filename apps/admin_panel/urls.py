from django.urls import path
from . import views
from . import file_upload_api

app_name = 'admin_panel'

urlpatterns = [
    path('', views.AdminDashboardView.as_view(), name='dashboard'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
    path('settings/test-email/', views.test_email_config, name='test_email'),
    path('settings/test-imap/', views.test_imap_config, name='test_imap'),
    path('license/', views.manage_license, name='manage_license'),
    path('audit-logs/', views.audit_logs_view, name='audit_logs'),

    # File Upload APIs
    path('api/upload-file/', file_upload_api.upload_file, name='upload_file'),
    path('api/upload-image/', file_upload_api.upload_image_for_editor, name='upload_image'),
]
