from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from users.forms import UserLoginForm, UserRegistrationForm
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
        'title': 'Вход',
        'content': 'Вход',
        'form': form
    }
    return render(request, 'users/login.html',context)

def logup(request):
    if request.method == 'POST':     
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            
            form.save()
            return HttpResponseRedirect(reverse('users:login'))
    else:      
        form = UserRegistrationForm()  
    
    
    context = {
        'title': 'Регистрация',
        'form': form ,
    }
    return render(request, 'users/logup.html',context)