from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from users.forms import UserLoginForm
from django.contrib import auth
from django.urls import reverse

def login(request):
    form = UserLoginForm()
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
    if form.is_valid():
        username = request.POST['username']   
        password = request.POST['password']
        user = auth.authenticate(username=username,password=password)
        if user:
            auth.login(request,user)
            return HttpResponseRedirect(reverse('main:index'))
        else:
            form = UserLoginForm()  
    
    context = {
        'title': 'Burnycom - Вход',
        'content': 'Вход',
        'form': form
    }
    return render(request, 'users/login.html',context)

def logup(request):
    context = {
        'title': 'Burnycom - Регистрация',
        'content': 'Регистрация'
    }
    return render(request, 'users/logup.html',context)