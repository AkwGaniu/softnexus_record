from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome),
    path('login', views.login),
    path('home', views.home),
    path('register', views.register),
    path('add_user', views.create_user)
]