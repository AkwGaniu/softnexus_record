import datetime
import calendar
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