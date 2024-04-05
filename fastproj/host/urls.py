from django.urls import path
from . import views
# from .views import client_created
from .views import create_client, display_clients, get_client, send_message

urlpatterns = [
    path('', views.index, name='index'),
    path('create_client/', create_client, name='create_client'),
    path('display_clients/', display_clients, name='display_clients'),
    path('get_client/<int:client_id>/', get_client, name='get_client'),
    path('send_message/<int:client_id>/', views.send_message, name='send_message'),
]
