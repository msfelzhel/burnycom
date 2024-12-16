from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.


def lk(request):
    context = {
        'title': 'Личный кабинет',
        'content': 'Личный кабинет'
    }
    return render(request, 'lk/profil.html',context)
