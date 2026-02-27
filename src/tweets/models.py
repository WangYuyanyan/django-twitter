
from django.conf import settings
from django.db import models
from django.utils import timezone

class Tweet(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete = models.SET_NULL, 
        null=True, 
        related_name='tweets',
    )
    content = models.CharField(max_length = 255)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def hours_to_now(self):
        delta = timezone.now() - self.created_at
        return int(delta.total_seconds() / 3600)
    
    def __str__(self):
        return f"{self.created_at} {self.user}: {self.content}"