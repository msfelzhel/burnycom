from django.contrib import admin
from django.urls import path,include




urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('main.urls', namespace ='main')),
    path('login/',include('users.urls', namespace ='users')),
    path('lk/',include('lk.urls', namespace ='lk')),
    path('task/',include('task.urls', namespace ='task')),
]
