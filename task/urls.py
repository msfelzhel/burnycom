from django.urls import path
from task.views import TaskListView

app_name = 'task'

urlpatterns = [
    path('',TaskListView.as_view(),name='task')  
]