from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
import json
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from account_book.models import Permission, Account, Client

# PERSONAL IMPORTS
from .utilities import util

def welcome(request):
  if not request.user.is_authenticated:
    return render(request, 'login.html')
  else:
    return render(request, 'home.html')


def register(request):
  if not request.user.is_authenticated:
    return render(request, 'register.html')
  else:
    return render(request, 'home.html')


def home(request):
  if request.user.is_authenticated:
    return render(request, 'home.html')
  else:
    return redirect('/')


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
          'user_image': False,
          'edit_permit': True,
          'delete_permit': True,
          'add_permit': True,
          'download_permit': True
        }
      else:
        permit = Permission.objects.filter(user=current_user.id)
        permit = list(permit.values(
        'user_id', 'add_permit', 'edit_permit', 
        'delete_permit', 'download_permit', 'user_image'
        ))

        user_permission = {}
        for user in permit:
          user_permission.update(user)

        print(user_permission)
        new_user_obj = {
          'username': current_user.username,
          'is_admin': current_user.is_superuser,
          'user_image': user_permission['user_image'],
          'edit_permit': user_permission['edit_permit'],
          'delete_permit': user_permission['delete_permit'],
          'add_permit': user_permission['add_permit'],
          'download_permit': user_permission['download_permit']
        }

      get_accounts = Account.objects.all()
      get_clients = Client.objects.all()

      client_records = list(get_clients.values(
      'id', 'client_name', 'client_email',
      'client_phone', 'service_offered',
      'amount_charged', 'amount_paid', 'balance_due',
      'qty', 'due_date', 'date'
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

class CreateUser(APIView):

  parser_classes = (MultiPartParser, )

  def post(self, request, format=None):
    try:
      if 'file' in request.FILES:
        user_image = request.FILES['file']
      else:
        user_image = False
      print(user_image)
      username = request.data['username']
      password = request.data['password']
      email = request.data['email']

      if User.objects.filter(username=username).exists():
        return JsonResponse({'reply': 'Username already exist'})
      elif  User.objects.filter(email=email).exists():
        return JsonResponse({'reply': 'Email already exist'})
      else:
        user = User(
          username = username,
          password = password,
          email = email,
          is_staff = True
        )
        user.set_password(password)
        user.save()
        if not user_image:
          set_permission = Permission(
            user = User(id=user.id),
          )
        else:
          set_permission = Permission(
            user = User(id=user.id),
            user_image = user_image
          )
        set_permission.save()
        return JsonResponse({'reply': 'success'})
    except EnvironmentError as e:
      print({'Error': e})


@api_view(['post'])
def user_login(request):
  try:
    username = request.data['username']
    password = request.data['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
      user_data = {'user': user.username}
      return JsonResponse({'reply': user_data})
    else:
      return JsonResponse({'reply':'access denied'})
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
    due_date = request.data['due_date']
    qty = request.data['qty']
    user = request.data['user']
    action = request.data['permit']
    current_date = util.user_friendly_date()

    if len(client_name) == 0 or len(client_email) == 0 or len(service_offered) == 0 or len(amount_charged) == 0:
      return JsonResponse({
        "reply": "fill required fields"
        })
    else:
      if util.is_permitted(user, action):
        balance_due = float(amount_charged) - float(amount_paid)
        balance_due = str(balance_due) + '0'
        balance_due =  util.format_price(balance_due)
        amount_charged = util.format_price(amount_charged)
        amount_paid = util.format_price(amount_paid)

        new_client_record = Client(
          client_name = client_name,
          client_email = client_email,
          client_phone = client_phone_num,
          service_offered = service_offered,
          amount_charged = amount_charged,
          amount_paid = amount_paid,
          balance_due = balance_due,
          qty = qty,
          due_date = due_date,
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
    qty = request.data['qty']
    due_date = request.data['due_date']
    client_id = request.data['id']
    user = request.data['user']
    action = request.data['permit']

    if len(client_name) == 0 or len(client_email) == 0 or len(service_offered) == 0 or len(amount_charged) == 0:
      return JsonResponse({
        "reply": "fill required fields"
        })
    else:      
      if util.is_permitted(user, action):
        balance_due = float(amount_charged) - float(amount_paid)
        balance_due = str(balance_due) + '0'
        balance_due =  util.format_price(balance_due)
        amount_charged = util.format_price(amount_charged)
        amount_paid = util.format_price(amount_paid)

        client = Client.objects.get(id = client_id)

        client.client_name = client_name
        client.client_email = client_email
        client.client_phone = client_phone_num
        client.service_offered = service_offered
        client.amount_charged = amount_charged
        client.amount_paid = amount_paid
        client.balance_due = balance_due
        client.qty = qty
        client.due_date = due_date


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
        amount = util.format_price(amount)
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
        amount = util.format_price(amount)

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


def generate_invoice(request):
  client_id = request.GET['id']
  client = Client.objects.get(id = client_id)
  invoice = {
    'id': client.id,
    'client_name': client.client_name,
    'clent_email': client.client_email,
    'client_phone': client.client_phone,
    'service_offered': client.service_offered,
    'amount_charged': client.amount_charged,
    'amount_paid': client.amount_paid,
    'balance_due': client.balance_due,
    'qty': client.qty,
    'due_date': client.due_date
  }
  
  context = {}
  context['invoice'] = json.dumps(invoice)
  return render(request, 'invoice.html', context)


from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.template.loader import get_template

from weasyprint import HTML

def html_to_pdf_view(request):
  client_id = request.GET['id']
  client = Client.objects.get(id = client_id)

  date = util.user_friendly_date()
  due_date = util.format_date(client.due_date)

  invoice = {
    'id': client.id,
    'client_name': client.client_name,
    'clent_email': client.client_email,
    'client_phone': client.client_phone,
    'service_offered': client.service_offered,
    'amount_charged': client.amount_charged,
    'amount_paid': client.amount_paid,
    'balance_due': client.balance_due,
    'qty': client.qty,
    'due_date': due_date,
    'date': date
  }

  html_template = render_to_string('pdf_invoice_template.html', {'invoice': invoice})
  pdf_file = HTML(string=html_template, base_url=request.build_absolute_uri()).write_pdf() 

  response = HttpResponse(pdf_file, content_type='application/pdf')
  response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
  return response


@api_view(['post'])
def test(request, user_slug, hash_slug):
  try:
    name = request.data.get('name', None)
    if name == None:
      print("No data attached")
    else:
      print(name)
    print(f"Yoooo {user_slug} YYYYoooo {hash_slug}")
    return JsonResponse({
      'error': 0,
      'message': "Good",
      "user_ip" : f"{request.META.get('REMOTE_ADDR', None)} {request.META.get('HTTP_USER_AGENT', '')}"
    })
  except EnvironmentError as error:
    print(error)