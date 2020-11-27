from django.db import models

# Create your models here.
class PyPIDeploy(models.Model):
    user_id = models.IntegerField()
    commit_id = models.UUIDField()
    