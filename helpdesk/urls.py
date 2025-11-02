"""
URL configuration for ML Gruppe Helpdesk project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('apps.accounts.urls')),
    path('tickets/', include('apps.tickets.urls')),
    path('kb/', include('apps.knowledge.urls')),
    path('chat/', include('apps.chat.urls')),
    # path('api/v1/', include('apps.api.urls')),  # Uncomment when REST framework is installed
    path('', include('apps.main.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = f"{settings.COMPANY_NAME} Helpdesk Administration"
admin.site.site_title = f"{settings.COMPANY_NAME} Helpdesk Administration"
admin.site.index_title = f"Willkommen im {settings.COMPANY_NAME} Helpdesk Admin"
