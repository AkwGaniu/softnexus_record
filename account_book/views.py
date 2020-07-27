from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from account_book.models import Permission, Account, Client

# PERSONAL IMPORTS
from .utilities import util

def welcome(request):
  if not request.user.is_authenticated:
    return render(request, 'login.html')
  else:
    return render(request, 'homeNew.html')

def register(request):
  if not request.user.is_authenticated:
    return render(request, 'register.html')
  else:
    return render(request, 'homeNew.html')

def home(request):
  if request.user.is_authenticated:
    return render(request, 'homeNew.html')
  else:
    return redirect('/')

@api_view(['post'])
def user_login(request):
  try:
    username = request.data['username']
    password = request.data['password']

    user = authenticate(request, username=username, password=password)
    if user is not None:
      # login(request, user)
      user_data = {'user': user.username}
      return JsonResponse({'reply': user_data})
      # return redirect('/homeNew?user='+ user.username)
    else:
      return JsonResponse({'reply':'access denied'})
  except EnvironmentError as e:
    print({'Error': e})


def logout_user(request):
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
          'add_permit': True,
          'download_permit': True
        }
      else:
        user_permission = Permission.objects.get(user=current_user.id)
        new_user_obj = {
          'username': current_user.username,
          'is_admin': current_user.is_superuser,
          'edit_permit': user_permission.edit_permit,
          'delete_permit': user_permission.delete_permit,
          'add_permit': user_permission.add_permit,
          'download_permit': user_permission.download_permit
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
    return redirect('/')


@api_view(['post'])
def create_user(request):
  try:
    username = request.data['username']
    password = request.data['password']
    email = request.data['email']

    users = User.objects.filter(username=username)
    if len(users) > 0:
      return JsonResponse({'reply': 'username already exist'})
    else:
      user = User(
        username = username,
        password = password,
        email = email,
        is_staff = True
      )
      user.set_password(password)
      user.save()
      set_permission = Permission(
        user = User(id=user.id)
      )
      set_permission.save()
      return JsonResponse({'reply': 'success'})
  except EnvironmentError as e:
    print({'Error': e})


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
    current_date = util.user_friendly_date()

    if len(client_name) == 0 or len(client_email) == 0 or len(service_offered) == 0 or len(amount_charged) == 0:
      return JsonResponse({
        "reply": "fill required fields"
        })
    else:
      if util.is_permitted(user, action):
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
        payload = util.reloadData(user)
        return JsonResponse({"reply": payload})
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
      if util.is_permitted(user, action):
        client = Client.objects.get(id = client_id)
    
        client.client_name = client_name
        client.client_email = client_email
        client.client_phone = client_phone_num
        client.service_offered = service_offered
        client.amount_charged = amount_charged
        client.amount_paid = amount_paid

        client.save()
        payload = util.reloadData(user)
        return JsonResponse({"reply": payload})
      else:
        return JsonResponse({
          "reply": "Access deniied"
          })
  except EnvironmentError as e:
    print({'Error': e})

  
@api_view(['post'])
def add_account_record(request):
  try:
    description = request.data['description']
    amount = request.data['amount']
    entry_type = request.data['entry_type']
    user = request.data['user']
    action = request.data['permit']
    current_date = util.user_friendly_date()

    if len(description) == 0 or len(amount) == 0 or len(entry_type) == 0:
      return JsonResponse({
        "reply": "fill required fields"
        })
    else:
      if util.is_permitted(user, action):
        new_account_record = Account(
          description = description,
          entry_type = entry_type,
          amount = amount,
          date = current_date
        )
        new_account_record.save()
        payload = util.reloadData(user)
        return JsonResponse({"reply": payload})
      else:
        return JsonResponse({
          "reply": "Access denied"
          })
  except EnvironmentError as e:
    print({'Error': e})


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
      if util.is_permitted(user, action):
        account = Account.objects.get(id = entry_id)
        account.description = description
        account.entry_type = entry_type
        account.amount = amount
        account.save()
        payload = util.reloadData(user)
        return JsonResponse({"reply": payload})
      else:
        return JsonResponse({
          "reply": "Access denied"
          })
  except EnvironmentError as e:
    print({'Error': e})


@api_view(['delete'])
def delete_record(request):
  try:
    table = request.data['table']
    del_id = request.data['id']
    user = request.data['user']
    action = request.data['permit']

    if util.is_permitted(user, action):
      if table == 'Client':
        record = Client.objects.get(id=del_id)
      elif table == 'Account':
        record = Account.objects.get(id=del_id)

      record.delete()
      
      payload = util.reloadData(user)
      return JsonResponse({"reply": payload})
    else:
      return JsonResponse({"reply": 'Access denied'})
  except EnvironmentError as e:
    print({'Error': e})


def user_permission(request):
  if request.user.is_authenticated:
    try:
      users_result = User.objects.filter()
      users = list(users_result.values('id', 'username', 'email', 'is_staff', 'is_superuser'))
      permissions_result = Permission.objects.filter()
      permissions = list(permissions_result.values(
        'user_id', 'add_permit', 'edit_permit', 
        'delete_permit', 'download_permit'
      ))

      list_of_users = []
      for user in users:
        if user['is_superuser']:
          continue
        for permit in permissions:
          if permit['user_id'] == user['id']:
            user.update({'permissions': permit})
        list_of_users.append(user)
      context = {}
      context['users'] = json.dumps(list_of_users)
      return render(request, 'users.html', context)
    except EnvironmentError as e:
      print({'Error': e})
  else:
    return  redirect('/')

@api_view(['put'])
def permit_user(request):
  try:
    admin = request.data['admin']
    user_id = request.data['user_id']
    action = request.data['permit_type']
    
    admin_user = User.objects.get(username=admin)
    if admin_user.is_superuser:
      permission = Permission.objects.get(user_id=user_id)
      if action == 'add_permit':
        permission.add_permit = not permission.add_permit
      elif action == 'edit_permit':
        permission.edit_permit = not permission.edit_permit
      elif action == 'delete_permit':
        permission.delete_permit = not permission.delete_permit
      elif action == 'download_permit':
        permission.download_permit = not permission.download_permit

      permission.save()
      
      payload = util.reloadUserData()
      return JsonResponse({"reply": payload})
    else:
      return JsonResponse({"reply": 'Access denied'})
  except EnvironmentError as e:
    print({'Error': e})


def export_record(request):
  if request.user.is_authenticated:
    try:
      record = request.GET['record']
      if record == 'account':
        file_name = 'Account Record'
        xlsx_data = util.write_account_to_excel()
      elif record == 'client':
        file_name = 'Client Record'
        xlsx_data = util.write_client_to_excel()

      response = HttpResponse(content_type='application/vnd.ms-excel')
      response['Content-Disposition'] = f'attachment; filename={file_name}.xlsX'
      response.write(xlsx_data)
      return response
    except EnvironmentError as e:
      print({'error': e})
  else:
    redirect('/')