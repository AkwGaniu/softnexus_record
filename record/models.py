from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Account_book(models.Model):
  description = models.CharField(max_length=1000),
  date = models.DateField(auto_now=False, auto_now_add=False),
  amount = models.FloatField(),
  entry_type = models.CharField(max_length=10)


class Client_payment(models.Model):
  client_name = models.CharField(max_length=100),
  client_email = models.EmailField(),
  client_phone = models.PositiveIntegerField(),
  service_offered = models.CharField(max_length=1500),
  amount = models.FloatField(),
  balance = models.FloatField(),
  date = models.DateField(auto_now=False, auto_now_add=False),



class Permission(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  edit_permit = models.BooleanField(default=False)
  delete_permit = models.BooleanField(default=False)
  add_permit = models.BooleanField(default=False)

  