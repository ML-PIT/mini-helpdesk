from django.urls import path
from . import views

app_name = 'knowledge'

urlpatterns = [
    path('', views.kb_list, name='list'),
    path('create/', views.kb_create, name='create'),
    path('<slug:slug>/', views.kb_detail, name='detail'),
    path('<slug:slug>/edit/', views.kb_edit, name='edit'),
]
