from django.urls import path, include
from . import views

urlpatterns = [
    path('rest-auth/', include('rest_auth.urls')),
    path('', views.welcome),
    path('user_login', views.user_login),
    path('home', views.home),
    path('get_data', views.get_data),
    path('register', views.register),
    path('register_user', views.create_user),
    path('add_client_record', views.add_client_record),
    path('update_client_record', views.update_client_record),
    path('add_account_record', views.add_account_record),
    path('update_account_record', views.update_account_record),
    path('delete_record', views.delete_record),
    path('logout_user', views.logout_user),
    path('user_permission', views.user_permission),
    path('permit_user', views.permit_user),
    path('export_record', views.export_record)
]
