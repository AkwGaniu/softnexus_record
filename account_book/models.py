from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Account(models.Model):
  description = models.CharField(max_length=1000)
  date = models.CharField(max_length=50)
  amount = models.CharField(max_length=20)
  entry_type = models.CharField(max_length=10)


class Client(models.Model):
  client_name = models.CharField(max_length=100)
  client_email = models.EmailField()
  client_phone = models.CharField(max_length=15)
  service_offered = models.CharField(max_length=1500)
  amount_charged = models.CharField(max_length=20)
  amount_paid = models.CharField(max_length=20)
  date = models.CharField(max_length=50)


class Permission(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  edit_permit = models.BooleanField(default=False)
  delete_permit = models.BooleanField(default=False)
  add_permit = models.BooleanField(default=False)

  