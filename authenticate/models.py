from django.db import models
import uuid

# Create your models here.
class Verify(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = models.IntegerField()
    code = models.IntegerField() # 0: Email Verify, 1: Forgot Password


class TwoFAUsage(models.Model):
    user_id = models.IntegerField()


class TwoFAToken(models.Model):
    user_id = models.IntegerField()
    code = models.CharField(max_length=7, unique=True)
    phone = models.TextField()


class TwoFA(models.Model):
    user_id = models.IntegerField()
    phone = models.TextField()


class AuthorizedDevice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = models.IntegerField()