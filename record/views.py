from django.shortcuts import render, redirect
from django.http import HttpResponse
import json
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from urlparams.redirect import param_redirect
from .models import Permission 

# Create your views here.
def welcome(request):
  return render(request, 'login.html')

def register(request):
  return render(request, 'register.html')


def login(request):
  try:
    username = request.POST['username']
    password = request.POST['password']

    if len(username) == 0 or len(password) == 0:
      error = 'Please provide your login details'
      error_obj = {
        'error': error
      }
      return render(request, 'login.html', error_obj)
    elif len(password) < 6:
      error = 'Please provide password of 6+ Characters'
      error_obj = {
        'error': error
      }
      return render(request, 'login.html', error_obj)
    else:
      user = authenticate(username=username, password=password)
      if user is not None:
        print('cool')
        context={}
        context["data"] = json.dumps({'name': username, 'password': password})
        print(user)
        return redirect('/home?user='+user.username)
        # return param_redirect(request, home, "EnnyGbash")
      else:
        print('Bad market')

  except EnvironmentError as e:
    print('Error: ' + e)


def home(request):
  try:
    username = request.GET['user']
    current_user = User.objects.get(username=username)    
    if current_user.is_superuser:
       new_user_obj = {
        'username': current_user.username,
        'is_admin': current_user.is_superuser,
      }
    else:
      user_permission = Permission.objects.get(user=current_user.id)
      new_user_obj = {
        'username': current_user.username,
        'is_admin': current_user.is_superuser,
        'edit_permit': user_permission.edit_permit,
        'delete_permit': user_permission.delete_permit,
        'add_permit': user_permission.add_permit
      }
    context = {}
    context['data'] = json.dumps(new_user_obj)
    return render(request, 'home.html', context)
  except EnvironmentError as e:
    print('Error: ' + e)


def create_user(request):
  try:
    username = request.POST['username']
    password = request.POST['password']
    email = request.POST['email']
    comfirm_pass = request.POST['comfirmpass']

    error_obj = {
      'error': ''
    }
    if len(username) == 0 or len(email) == 0:
      error_obj.update({'error': 'Please fill out the form'})
      return render(request, 'register.html', error_obj)
    elif len(password) < 6:
      error_obj.update({'error': 'Please provide a password of 6+ characters'})
      return render(request, 'register.html', error_obj)
    elif password != comfirm_pass:
      error_obj.update({'error': 'Password fields does not match'})
      return render(request, 'register.html', error_obj)
    else:
      user = User(
        username = username,
        password = password,
        email = email,
      )
      user.set_password(password)
      user.save()
      set_permission = Permission(
        user = User(id=user.id)
      )
      set_permission.save() 
      error_obj.update({'error': 'success'})
      return render(request, 'login.html', error_obj)
  except EnvironmentError as e:
    print('Error: ' + e)
  # except:
  #   return HttpResponse('Oopss, Something went wrong')