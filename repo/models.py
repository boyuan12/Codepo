from django.db import models
from django.utils import timezone

# Create your models here.
class PyPIDeploy(models.Model):
    user_id = models.IntegerField()
    commit_id = models.UUIDField()
    url = models.CharField(max_length=255, null=True)
    timestamp = models.DateTimeField(default=timezone.now)
    project = models.CharField(max_length=100, null=True)
    success = models.BooleanField()
    message = models.TextField(null=True)
    version = models.CharField(max_length=10, null=True)

class HerokuDeploy(models.Model):
    user_id = models.IntegerField()
    repo_id = models.IntegerField()
    commit_id = models.UUIDField()
    timestamp = models.DateTimeField(default=timezone.now)
