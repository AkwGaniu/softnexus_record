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

    return payload
  except EnvironmentError as e:
    print({'Error': e})


def reloadUserData():
  try:
    users_result = User.objects.filter()
    users = list(users_result.values('id', 'username', 'email', 'is_staff', 'is_superuser'))
    permissions_result = Permission.objects.filter()
    permissions = list(permissions_result.values('user_id', 'add_permit', 'edit_permit', 'delete_permit'))
    list_of_users = []
    for user in users:
      for permit in permissions:
        if permit['user_id'] == user['id']:
          user.update({'permissions': permit})
        elif user['is_superuser']:
          user.update({'permissions': {'add_permit': True, 'delete_permit': True, 'edit_permit': True}})
      list_of_users.append(user)
    context = {}
    context['users'] = list_of_users
    return  context
  except EnvironmentError as e:
    print({'Error': e})


def account_data():
  get_accounts = Account.objects.all()

  account_records = list(get_accounts.values(
    'id', 'description', 'date', 'amount', 'entry_type'
  ))
  return account_records


def WriteToExcel():
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