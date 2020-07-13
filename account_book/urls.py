from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome),
    path('login', views.login),
    path('home', views.home),
    path('register', views.register),
    path('add_user', views.create_user),
    path('add_acc_record', views.add_acc_record), 
    path('add_client_record', views.add_client_record)
]