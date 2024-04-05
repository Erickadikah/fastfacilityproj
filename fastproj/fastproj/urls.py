"""
URL configuration for faciltyapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from register import views as v
# from django.contrib.auth.views import LogoutView
from host.views import create_client, display_clients, delete_client, guest_login, get_documents, client_logout, documents
from register.views import logout_view
from django.conf.urls.static import static
from django.conf import settings
# from guest.views import user_profile
from register.views import user
# from Guest.views import 
from host.views import index, get_client, delete_file, download_file, get_uploaded_documents, upload_file, get_user, display_users, get_all_clients, send_message, get_messages, delete_message, update_client, delete_document
from guest.views import upload_document

urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload_file/<int:user_id>/', upload_file, name='upload_file'),
    path('guest/', include('guest.urls')),
    path('host/', index, name='host'),
    path('', include('home.urls')),
    path('host/', include('host.urls')),
    path('register/', v.register, name='register'),
    path('login/', v.login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('create_client/', create_client, name='create_client' ),
    path('display_clients/', display_clients, name='display_clients'),
    path('delete_client/<int:id>/', delete_client, name='delete_client'),
    path('guest_login/', guest_login, name='guest_login'),
    path('user/<int:user_id>/', user, name='user_detail'),
    # path('get_client/<int:user_id>/<int:client_id>/', get_client, name='get_client'),
    path('get_user/<int:user_id>/', get_user, name='get_user'),
    path('display_users/', display_users, name='display_users'),
    path('get_all_clients/', get_all_clients, name='get_all_clients'),
    path('upload/<int:client_id>/', upload_document, name='upload_document'),
    path('send_message/<int:client_id>/', send_message, name='send_message'),
    path('get_messages/<int:client_id>/', get_messages, name='get_messages'),
    path('delete_message/<int:message_id>/', delete_message, name='delete_message'),
    path('update_client/<int:client_id>/', update_client, name='update_client'),
    path('get_documents/<int:user_id>/', get_documents, name='get_documents'),
    path('delete_document/<int:document_id>/', delete_document, name='delete_document'),
    path(' client_logout/',  client_logout, name='client_logout'),
    path('document/<int:user_id>/', documents, name='document'),
    path('get_uploaded_documents/<int:client_id>/', get_uploaded_documents, name='get_uploaded_documents'),
    path('download/<int:user_id>/', download_file, name='download_file'),
    path('get_client/<int:client_id>/', get_client, name='get_client'),
    path('delete_file/<int:file_id>/', delete_file, name='delete_file')
    ]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)