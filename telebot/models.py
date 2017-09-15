from lib.models import Staff
from django.utils import timezone
from django.db import models

# Create your models here.
class AuthorizedUser(models.Model):
    firstname = models.CharField(max_length=30, null=True)
    secondname = models.CharField(max_length=30, null=True)
    user_name = models.CharField(max_length=30, null=True)
    user_id = models.IntegerField(unique=True)
    telephone = models.BigIntegerField(unique=True)
    authorized = models.BooleanField(default=False)

class Schedule(models.Model):
    name = models.CharField(max_length=30)
    master = models.ForeignKey(Staff, null=True, blank=True)
    date_start = models.DateTimeField(default=timezone.now)
    date_accept = models.DateTimeField(blank=True, null=True)
    date_close = models.DateTimeField(blank=True, null=True)
    accepted = models.BooleanField(default=False)
