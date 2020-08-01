from django.db import models

# Create your models here.
class OAuth(models.Model):
    user_id = models.IntegerField()
    name = models.CharField(max_length=50)
    client_id = models.CharField(max_length=30)
    client_secret = models.CharField(max_length=50)

class Uri(models.Model):
    client_id = models.CharField(max_length=30)
    redirect_uri = models.URLField()

class Token(models.Model):
    client_id = models.CharField(max_length=30)
    token = models.CharField(max_length=100)
    user_id = models.IntegerField() # know which user's information to fetch

class Access_Code(models.Model):
    access_code = models.CharField(max_length=65)
    user_id = models.IntegerField()