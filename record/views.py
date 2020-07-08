from django.shortcuts import render
from django.http import HttpResponse
import json

# Create your views here.
def welcome(request):
  return render(request, 'login.html')


def login(request):
  username = request.POST['username']
  password = request.POST['password']

  if len(username) == 0 or len(password) == 0:
    error = 'Please provide your login details'
    error_obj = {
      'error': error
    }
    return render(request, 'login.html', error_obj)
  else:
    context={}
    context["data"] = json.dumps({'name': username, 'password': password})
    print(context)
    return render(request, 'home.html', context)