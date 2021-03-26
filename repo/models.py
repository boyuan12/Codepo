from django.db import models
from django.db.models.fields import DateTimeField
from django.utils import timezone


# Create your models here.
class PyPIDeploy(models.Model):
    user_id = models.IntegerField()
    commit_id = models.UUIDField()
    

class HerokuDeploy(models.Model):
    user_id = models.IntegerField()
    repo_id = models.IntegerField()
    commit_id = models.UUIDField()
    timestamp = models.DateTimeField(default=timezone.now)
