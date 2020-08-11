import datetime
import calendar
import io
import xlsxwriter
from django.http import HttpResponse
from django.contrib.auth.models import User
from account_book.models import Permission 
from account_book.models import Permission, Account, Client


def user_friendly_date():
  date = datetime.datetime.now()
  current_date = date.day
  current_year = date.year
  # day_name = calendar.day_name[date.weekday()]
  month_name = calendar.month_name[date.month]
  user_date = month_name +' '+ str(current_date) +', '+ str(current_year)
  return user_date


def format_date(date):
  new_date = date.split('-')
  year, month, day = new_date
  month_name = calendar.month_name[int(month)]
  formated_date = month_name +' '+ day +', '+ year
  return formated_date


def format_price(num):
  price = num[:-3]
  if len(price) < 4:
    formated_price = num
  elif len(price) == 4:
    formated_price = f"{price[0:1]},{price[1:]}.00"
  elif len(price) == 5:
    formated_price = f"{price[0:2]},{price[2:]}.00"
  elif len(price) == 6:
    formated_price = f"{price[0:3]},{price[3:]}.00" 
  elif len(price) == 7:
    formated_price = f"{price[0:1]},{price[1:4]},{price[4:]}.00"
  elif len(price) == 8:
    formated_price = f"{price[0:2]},{price[2:5]},{price[5:]}.00"
  elif len(price) == 9:
    formated_price = f"{price[0:3]},{price[3:6]},{price[6:]}.00"
  elif len(price) == 10:
    formated_price = f"{price[0:1]},{price[1:4]},{price[4:7]},{price[7:]}.00"
  return formated_price

def is_permitted(user, action):
  current_user = User.objects.get(username=user)
  user_is_permitted = current_user.is_superuser
  if user_is_permitted:
    return True
  else:
    get_permit = Permission.objects.get(user_id=current_user.id)
    if action == 'add_permit':
      if get_permit.add_permit:
        return True
      else:
        return False
    elif action == 'edit_permit':
      if get_permit.edit_permit:
        return True
      else:
        return False
    elif action == 'delete_permit':
      if get_permit.delete_permit:
        return True
      else:
        return False
    else:
      return False


def reloadData(username):
  try:
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
      user_permission = Permission.objects.get(user=current_user.id)
      new_user_obj = {
        'username': current_user.username,
        'is_admin': current_user.is_superuser,
        'user_image': user_permission.user_image,
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

    return payload
  except EnvironmentError as e:
    print({'Error': e})


def reloadUserData():
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
    context['users'] = list_of_users
    return  context
  except EnvironmentError as e:
    print({'Error': e})


def account_data():
  try:
    get_accounts = Account.objects.all()

    account_records = list(get_accounts.values(
      'id', 'description', 'date', 'amount', 'entry_type'
    ))
    return account_records
  except EnvironmentError as e:
    print({'Error': e})

def client_data():
  try:
    get_clients = Client.objects.all()

    client_records = list(get_clients.values(
      'id', 'client_name', 'client_email',
      'client_phone', 'service_offered',
      'amount_charged', 'amount_paid', 'date'
    ))
    return client_records
  except EnvironmentError as e:
    print({'Error': e})

def write_account_to_excel():
  output = io.BytesIO()
  workbook = xlsxwriter.Workbook(output)
  worksheet_s = workbook.add_worksheet("Account record")

  title = workbook.add_format({
    'bold': True,
    'font_size': 14,
    'align': 'center',
    'valign': 'vcenter'
  })
  header = workbook.add_format({
      'bg_color': '#F7F7F7',
      'color': 'black',
      'align': 'center',
      'valign': 'top',
      'border': 1
  })
  cell_center = workbook.add_format({
    'align': 'center',
    'valign': 'bottom',
  })
  cell = workbook.add_format({
    'align': 'left',
    'valign': 'bottom',
  })

  title_text = "SoftNexus Account Record"
  worksheet_s.merge_range('A1:E1', title_text, title)

  worksheet_s.write(1, 0, "S/N", header)
  worksheet_s.write(1, 1, "DESCRIPTION", header)
  worksheet_s.write(1, 2, "ENTRY TYPE", header)
  worksheet_s.write(1, 3, "AMOUNT", header)
  worksheet_s.write(1, 4, "DATE", header)

  # Here we will adding the code to add data
  account_record = account_data()
  description_col_width = 15
  for idx, data in enumerate(account_record):
    row = 2 + idx
    worksheet_s.write_number(row, 0, idx + 1, cell_center)
    worksheet_s.write_string(row, 1, data['description'], cell)
    if len(data['description']) > description_col_width:
      description_col_width = len(data['description'])
    worksheet_s.write(row, 2, data['entry_type'], cell)
    worksheet_s.write(row, 3, '#'+data['amount'], cell)
    worksheet_s.write(row, 4, data['date'], cell)
  
  worksheet_s.set_column('B:B', description_col_width)
  worksheet_s.set_column('C:C', 15)
  worksheet_s.set_column('D:D', 15)
  worksheet_s.set_column('E:E', 15)

  workbook.close()
  xlsx_data = output.getvalue()
  return xlsx_data


def write_client_to_excel():
  output = io.BytesIO()
  workbook = xlsxwriter.Workbook(output)
  worksheet_s = workbook.add_worksheet("Client record")

  title = workbook.add_format({
    'bold': True,
    'font_size': 14,
    'align': 'center',
    'valign': 'vcenter'
  })
  header = workbook.add_format({
      'bg_color': '#F7F7F7',
      'color': 'black',
      'align': 'center',
      'valign': 'top',
      'border': 1
  })
  cell_center = workbook.add_format({
    'align': 'center',
    'valign': 'bottom',
  })
  cell = workbook.add_format({
    'align': 'left',
    'valign': 'bottom',
  })

  title_text = "SoftNexus Client Entry Record"
  worksheet_s.merge_range('A1:H1', title_text, title)

  worksheet_s.write(1, 0, "S/N", header)
  worksheet_s.write(1, 1, "SERVICE OFFERED", header)
  worksheet_s.write(1, 2, "CLIENT NAME", header)
  worksheet_s.write(1, 3, "EMAIL", header)
  worksheet_s.write(1, 4, "PHONE NUMBER", header)
  worksheet_s.write(1, 5, "AMOUNT CHARGED", header)
  worksheet_s.write(1, 6, "AMOUNT PAID", header)
  worksheet_s.write(1, 7, "DATE", header)


  account_record = client_data()
  service_col_width = 15
  email_col_width = 15
  name_col_width = 15
  for idx, data in enumerate(account_record):
    row = 2 + idx
    worksheet_s.write_number(row, 0, idx + 1, cell_center)
    worksheet_s.write_string(row, 1, data['service_offered'], cell)
    if len(data['service_offered']) > service_col_width:
      service_col_width = len(data['service_offered'])
    worksheet_s.write(row, 2, data['client_name'], cell)
    if len(data['client_name']) > name_col_width:
      name_col_width = len(data['client_name'])
    worksheet_s.write(row, 3, data['client_email'], cell)
    if len(data['client_email']) > email_col_width:
      email_col_width = len(data['client_email'])
    worksheet_s.write(row, 4, data['client_phone'], cell)
    worksheet_s.write(row, 5, '#'+data['amount_charged'], cell)
    worksheet_s.write(row, 6, '#'+data['amount_paid'], cell)
    worksheet_s.write(row, 7, data['date'], cell)
  
  worksheet_s.set_column('B:B', service_col_width)
  worksheet_s.set_column('C:C', name_col_width+1)
  worksheet_s.set_column('D:D', email_col_width+1)
  print(f'email col width {email_col_width}')
  worksheet_s.set_column('E:E', 15)
  worksheet_s.set_column('F:F', 17)
  worksheet_s.set_column('G:G', 15)
  worksheet_s.set_column('H:H', 15)

  workbook.close()
  xlsx_data = output.getvalue()
  return xlsx_data

