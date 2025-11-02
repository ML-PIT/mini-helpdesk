from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Public endpoints for chat widget
    path('widget/', views.chat_widget, name='widget'),
    path('widget-data/', views.widget_data, name='widget_data'),
    path('api/start/', views.start_chat, name='start_chat'),
    path('api/send/', views.send_message, name='send_message'),
    path('api/messages/<str:session_id>/', views.get_messages, name='get_messages'),
    
    # Agent endpoints
    path('dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('api/take/<str:session_id>/', views.agent_take_chat, name='agent_take_chat'),
    path('api/agent/send/<str:session_id>/', views.agent_send_message, name='agent_send_message'),
    path('api/end/<str:session_id>/', views.end_chat, name='end_chat'),
    path('session/<str:session_id>/', views.chat_detail, name='chat_detail'),
]