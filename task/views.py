from django.views.generic import ListView
from task.models import Task
from django.contrib.auth.mixins import LoginRequiredMixin

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        # Получаем текущего пользователя
        username = self.request.user.username
        # Фильтруем задачи с JOIN по имени пользователя
        return Task.objects.select_related('user').filter(
            user__username=username
        ).order_by('-created_at')
