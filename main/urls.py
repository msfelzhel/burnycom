from django.urls import path
from main import views

app_name = 'main'

urlpatterns = [
    path('',views.index,name='index'),
    path('matem/',views.matem,name='matem'),
    path('inf/',views.inf,name='inf'),
]
