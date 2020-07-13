import datetime
import calendar
from django.contrib.auth.models import User
from account_book.models import Permission 


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
  print(action)
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