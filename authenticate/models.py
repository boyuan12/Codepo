from django.db import models
import uuid

# Create your models here.
class Verify(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = models.IntegerField()
    code = models.IntegerField() # 0: Email Verify, 1: Forgot Password