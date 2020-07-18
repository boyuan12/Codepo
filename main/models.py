from django.db import models

# Create your models here.
class Repository(models.Model):
    user_id = models.IntegerField()
    name = models.CharField(max_length=100)
    description = models.TextField()
    status = models.IntegerField()

class File(models.Model):
    repo_id = models.IntegerField()
    filename = models.CharField(max_length=100)
    directory_id = models.IntegerField()
    url = models.CharField(max_length=500)

class Directory(models.Model):
    repo_id = models.IntegerField()
    dir_id = models.IntegerField() # keep track which subdir it belongs
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)