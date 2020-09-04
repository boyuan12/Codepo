
from django.db import models
from django.utils.timezone import now
from django.contrib.postgres.fields import JSONField

# Create your models here.
class Repository(models.Model):
    user_id = models.IntegerField()
    name = models.CharField(max_length=100)
    description = models.TextField()
    status = models.IntegerField()


class File(models.Model):
    repo_id = models.IntegerField()
    filename = models.CharField(max_length=100)
    subdir = models.IntegerField()
    url = models.CharField(max_length=500)
    branch = models.CharField(max_length=20)
    path = models.CharField(max_length=255)


class Directory(models.Model):
    repo_id = models.IntegerField()
    subdir = models.IntegerField()
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    branch = models.CharField(max_length=100)


class Profile(models.Model):
    user_id = models.IntegerField()
    description = models.TextField()
    organization = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    website = models.URLField()
    avatar = models.URLField()


class Follows(models.Model):
    user_id = models.IntegerField()
    following = models.IntegerField()


class Branch(models.Model):
    repo_id = models.IntegerField()
    name = models.CharField(max_length=20)


# class Commit(models.Model):
#     repo_id = models.IntegerField()
#     timestamp = models.DateTimeField(auto_now=True)
#     user_message = models.TextField()
#     changes = JSONField()


class Star(models.Model):
    user_id = models.IntegerField()
    repo_id = models.IntegerField()