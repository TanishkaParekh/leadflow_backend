from django.db import models
from leads.models import *

class Task(models.Model):
    title = models.CharField(max_length=255)
    due_date = models.DateTimeField()
    is_completed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title