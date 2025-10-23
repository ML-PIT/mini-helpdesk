from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('', views.ticket_list, name='list'),
    path('create/', views.ticket_create, name='create'),
    path('statistics/', views.statistics_dashboard, name='statistics'),
    path('api/search-customers/', views.search_customers_api, name='search_customers_api'),
    path('<int:pk>/', views.ticket_detail, name='detail'),
    path('<int:pk>/assign/', views.ticket_assign, name='assign'),
    path('<int:pk>/escalate/', views.ticket_escalate, name='escalate'),
    path('<int:pk>/close/', views.ticket_close, name='close'),
]
