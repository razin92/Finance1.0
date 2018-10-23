from django.db import models

# Create your models here.
class SubscriberRequest(models.Model):
    request_id = models.IntegerField(default=0, unique=True)
    request_pk = models.CharField(max_length=50, unique=True)
    ops_date = models.DateTimeField(default=None, null=True, blank=True, auto_now=False)
    date = models.DateTimeField(auto_now=True)
    request_status = models.PositiveSmallIntegerField(default=1)
    request_work = models.CharField(default='нет описания', max_length=100)
    request_address = models.CharField(default='q-b-a', max_length=50)
