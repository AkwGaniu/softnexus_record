from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from urlparams.redirect import param_redirect
from rest_framework.decorators import api_view
from account_book.models import Permission, Account, Client
from .utilities.utilities import user_friendly_date, is_permitted, reloadData


# Create your views here.
def welcome(request):
  if not request.user.is_authenticated:
    return render(request, 'login.html')
  else:
    return render(request, 'home.html')

def register(request):
  return render(request, 'register.html')

def home(request):
  if request.user.is_authenticated:
    return render(request, 'home.html')
  else:
    return render(request, '404.html')

@api_view(['post'])
def user_login(request):
  try:
    username = request.data['username']
    password = request.data['password']

    user = authenticate(request, username=username, password=password)
    if user is not None:
      login(request, user)
      user_data = {'user': user.username}
      return JsonResponse({'reply': user_data})
    else:
      return JsonResponse({'reply':'access denied'})
  except EnvironmentError as e:
    print('Error: ' + e)


def logout_user(request):
  print('herefdfdfdjfdjdjfjdkjf')
  logout(request)
  return redirect('/')


def get_data(request):
  if request.user.is_authenticated:
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
      return JsonResponse({'reply': payload})
    except EnvironmentError as e:
      print('Error: ' + e)
  else:
    return render(request, '404.html')


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
          "reply": "Access denied"
          })
  except EnvironmentError as e:
    print('Error: ' + e)


@api_view(['put'])
def update_client_record(request):
  try:
    client_name = request.data['name']
    client_phone_num = request.data['phone']
    client_email = request.data['email']
    service_offered = request.data['service']
    amount_charged = request.data['amount_charged']
    amount_paid = request.data['amount_paid']
    client_id = request.data['id']
    user = request.data['user']
    action = request.data['permit']

    if len(client_name) == 0 or len(client_email) == 0 or len(service_offered) == 0 or len(amount_charged) == 0:
      return JsonResponse({
        "reply": "fill required fields"
        })
    else:      
      if is_permitted(user, action):
        client = Client.objects.get(id = client_id)
     
        client.client_name = client_name
        client.client_email = client_email
        client.client_phone = client_phone_num
        client.service_offered = service_offered
        client.amount_charged = amount_charged
        client.amount_paid = amount_paid

        client.save()
        payload = reloadData(user)
        return JsonResponse({"reply": payload})
      else:
        return JsonResponse({
          "reply": "Access deniied"
          })
  except EnvironmentError as e:
    print('Error: ' + e)

  
@api_view(['post'])
def add_account_record(request):
  try:
    description = request.data['description']
    amount = request.data['amount']
    entry_type = request.data['entry_type']
    user = request.data['user']
    action = request.data['permit']
    current_date = user_friendly_date()

    if len(description) == 0 or len(amount) == 0 or len(entry_type) == 0:
      return JsonResponse({
        "reply": "fill required fields"
        })
    else:
      if is_permitted(user, action):
        new_account_record = Account(
          description = description,
          entry_type = entry_type,
          amount = amount,
          date = current_date
        )
        new_account_record.save()
        payload = reloadData(user)
        return JsonResponse({"reply": payload})
      else:
        return JsonResponse({
          "reply": "Access denied"
          })
  except EnvironmentError as e:
    print('Error: ' + e)


@api_view(['put'])
def update_account_record(request):
  try:
    description = request.data['description']
    amount = request.data['amount']
    entry_type = request.data['entry_type']
    user = request.data['user']
    action = request.data['permit']
    entry_id = request.data['id']

    if len(description) == 0 or len(amount) == 0 or len(entry_type) == 0:
      return JsonResponse({
        "reply": "fill required fields"
        })
    else:
      if is_permitted(user, action):
        account = Account.objects.get(id = entry_id)
        print(account.id)
        account.description = description
        account.type = entry_type
        account.amount = amount
        print(account.id)
        account.save()
        payload = reloadData(user)
        return JsonResponse({"reply": payload})
      else:
        return JsonResponse({
          "reply": "Access denied"
          })
  except EnvironmentError as e:
    print('Error: ' + e)

@api_view(['delete'])
def delete_record(request):
  try:
    print(request.data)
    table = request.data['table']
    del_id = request.data['id']
    user = request.data['user']
    action = request.data['permit']

    if is_permitted(user, action):
      if table == 'Client':
        record = Client.objects.get(id=del_id)
      elif table == 'Account':
        record = Account.objects.get(id=del_id)

      record.delete()
      
      payload = reloadData(user)
      return JsonResponse({"reply": payload})
    else:
      return JsonResponse({"reply": 'Access denied'})
  except EnvironmentError as e:
    print('Error: ' + e)