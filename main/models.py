from django.db import models
from django.utils.timezone import now
from django.contrib.postgres.fields import JSONField
import uuid
import datetime


# Create your models here.
class Repository(models.Model):
    user_id = models.IntegerField()
    name = models.CharField(max_length=100)
    description = models.TextField()
    status = models.IntegerField()
    fork = models.IntegerField(null=True) # if it's forked, origin repo id.


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


class Issue(models.Model):
    issue_id = models.IntegerField()
    user_id = models.IntegerField()
    repo_id = models.IntegerField()
    title = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    status = models.IntegerField(default=0) # 0: open, 1: closed


class Tags(models.Model):
    repo_id = models.IntegerField()
    issue_id = models.IntegerField()
    name = models.CharField(max_length=20)


class Issue_Comment(models.Model):
    repo_id = models.IntegerField()
    issue_id = models.IntegerField()
    user_id = models.IntegerField()
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    special = models.IntegerField(null=True, default=None) # 0: issue closed, 1: issue reopened


class Commit(models.Model):
    commit_id = models.CharField(primary_key=True, max_length=100)
    repo_id = models.IntegerField()
    user_id = models.IntegerField()
    message = models.CharField(max_length=100)
    branch = models.CharField(max_length=20, default="master")
    timestamp = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)


class Commit_File(models.Model):
    commit_id = models.TextField()
    url = models.TextField(null=True)
    code = models.IntegerField(null=True) # 0: deleted
    path = models.CharField(null=True, max_length=255)