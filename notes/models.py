from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Note(models.Model):
    class TaskStatus:
        NS = "NOT STARTED"
        IN = "IN_PROGRESS"
        COM = "COMPLETED"

        CHOICES = (
            (NS, "Not Started"),
            (IN, "In Progress"),
            (COM, "Completed"),
        )
    status = models.CharField(choices=TaskStatus.CHOICES, default=TaskStatus.NS, max_length=20)
    title = models.CharField(max_length=100)
    memo = models.CharField(max_length=280, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")
    review = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.title}"