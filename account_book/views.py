from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from urlparams.redirect import param_redirect
from rest_framework.decorators import api_view
from account_book.models import Permission, Account, Client
from .utilities.utilities import user_friendly_date, is_permitted


# Create your views here.
def welcome(request):
  return render(request, 'login.html')

def register(request):
  return render(request, 'register.html')


def login(request):
  try:
    error_obj = {
      'error': ''
    }
    username = request.POST['username']
    password = request.POST['password']

    if len(username) == 0 or len(password) == 0:
      error_obj.update({'error':'Please provide your login details'})
      return render(request, 'login.html', error_obj)
    elif len(password) < 6:
      error_obj.update({'error':'Please provide password of 6+ Characters'})
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
        error_obj.update({'error':'Invalid login credentials'})
        return render(request, 'login.html', error_obj)
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
        'edit_permit': True,
        'delete_permit': True,
        'add_permit': True
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

    get_accounts = Account.objects.all()
    get_clients = Client.objects.all()

    client_records = list(get_clients.values(
      'id', 'client_name', 'client_email',
      'client_phone', 'service_offered',
      'amount_charged', 'amount_paid', 'date'
    ))
    account_records = list(get_accounts.values(
      'id', 'description', 'date', 'amount', 'entry_type'
    ))
    payload = {
      'user': new_user_obj,
      'client_record': client_records,
      'account_record': account_records
    }
    context = {}
    context['data'] = json.dumps(payload)

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

@api_view(['post'])
def add_acc_record(request):
  try:
    print(request.data)

    return JsonResponse({"reply":"Cool"})
  except EnvironmentError as e:
    print('Error: ' + e)

@api_view(['post'])
def add_client_record(request):
  try:
    client_name = request.data['name']
    client_phone_num = request.data['phone']
    client_email = request.data['email']
    service_offered = request.data['service']
    amount_charged = request.data['amount_charged']
    amount_paid = request.data['amount_paid']
    user = request.data['user']
    action = request.data['permit']
    current_date = user_friendly_date()

    if len(client_name) == 0 or len(client_email) == 0 or len(service_offered) == 0 or len(amount_charged) == 0:
      return JsonResponse({
        "reply": "fill required fields"
        })
    else:
      if is_permitted(user, action):
        new_client_record = Client(
          client_name = client_name,
          client_email = client_email,
          client_phone = client_phone_num,
          service_offered = service_offered,
          amount_charged = amount_charged,
          amount_paid = amount_paid,
          date = current_date
        )
        new_client_record.save()
        return JsonResponse({"reply": "success"})
      else:
        return JsonResponse({
          "reply": ":) You need admin permission to perform this operation"
          })
  except EnvironmentError as e:
    print('Error: ' + e)


