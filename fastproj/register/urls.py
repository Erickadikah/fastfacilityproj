from django.urls import path
from . import views, user_detail
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),  # This maps the root URL to the index view
    path('register/', views.register, name='register'),  # Add this line to map /register URL to the register view
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('user/<int:user_id>/', user_detail, name='user_detail'),
]