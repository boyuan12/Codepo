from django.db import models
from django.utils import timezone
import django

# Create your models here.
class PyPIDeploy(models.Model):
    user_id = models.IntegerField()
    commit_id = models.UUIDField()
    url = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=django.utils.timezone.now)
    project = models.CharField(max_length=100)

