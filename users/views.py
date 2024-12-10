from django.shortcuts import render
from django.http import HttpResponse

def login(request):
    context = {
        'title': 'Burnycom - Вход',
        'content': 'Вход'
    }
    return render(request, 'users/login.html',context)

def logup(request):
    context = {
        'title': 'Burnycom - Регистрация',
        'content': 'Регистрация'
    }
    return render(request, 'users/logup.html',context)