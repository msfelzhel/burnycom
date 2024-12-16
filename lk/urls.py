from django.urls import path
from lk import views

app_name = 'lk'

urlpatterns = [
    path('',views.lk,name='lk')  
]