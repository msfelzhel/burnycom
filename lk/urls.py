from django.urls import path
from lk import views
from django.contrib.auth.views import LogoutView

app_name = 'lk'

urlpatterns = [
    path('',views.lk,name='lk'),
    path('logout/',LogoutView.as_view(next_page='/'),name='logout')  
]