from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    context = {
        'title': 'Burnycom - Главная',
        'content': 'Главная страница'
    }
    return render(request, 'main/index.html',context)

def matem(request):
    context = {
        'title': 'Burnycom - Математика',
        'content': 'Математика'
    }
    return render(request, 'main/matem.html' ,context)
def inf(request):
    context = {
        'title': 'Burnycom - Информатика',
        'content': 'Информатика'
    }
    return render(request, 'main/inf.html' ,context)
  
def contacts(request):
    context = {
        'title': 'Burnycom - Контакты',
        'content': 'Контакты'
    }
    return render(request, 'main/contacts.html' ,context)