import datetime
import calendar
import xlwt
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


def WriteToExcel():
	#creating workbook
	wb = xlwt.Workbook(encoding='utf-8')

	#adding sheet
	ws = wb.add_sheet("sheet1")

	# Sheet header, first row
	row_num = 0

	font_style = xlwt.XFStyle()
	# headers are bold
	font_style.font.bold = True

	#column header names, you can use your own headers here
	columns = ['Column 1', 'Column 2', 'Column 3', 'Column 4', ]

	#write column headers in sheet
	for col_num in range(len(columns)):
		ws.write(row_num, col_num, columns[col_num], font_style)

	# Sheet body, remaining rows
	font_style = xlwt.XFStyle()

	#get your data, from database or from a text file...
	data = get_data() #dummy method to fetch data.
	for my_row in data:
		row_num = row_num + 1
		ws.write(row_num, 0, my_row.name, font_style)
		ws.write(row_num, 1, my_row.start_date_time, font_style)
		ws.write(row_num, 2, my_row.end_date_time, font_style)
		ws.write(row_num, 3, my_row.notes, font_style)

	wb.save(response)
	return response


def account_data():
  get_accounts = Account.objects.all()

  account_records = list(get_accounts.values(
    'id', 'description', 'date', 'amount', 'entry_type'
  ))
  return account_records

  # # output = StringIO.StringIO()
  # workbook = xlsxwriter.Workbook()

  # # Write some data here
  # workbook.add_worksheet('Account')
  # workbook.close()
  # # xlsx_data = output.getvalue()
  # return  workbook