from django.shortcuts import render
from django.http import HttpResponse



def task(request):
    context = {
        'title': 'Задачи',
        'content': 'Задачи'
    }
    return render(request, 'task/task.html',context)

# Create your views here.
