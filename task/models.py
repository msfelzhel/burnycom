from django.db import models
from django.conf import settings

class Task(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    task_text = models.TextField()
    created_at = models.DateTimeField()

    class Meta:
        db_table = 'tasks'  # Указываем существующую таблицу
        managed = False  # Не управляем этой таблицей, так как она уже существует
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

    def __str__(self):
        return f"Задача {self.id} для {self.user.username}"
