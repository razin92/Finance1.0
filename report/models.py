from django.db import models
from lib.models import Pouch, Person, Category

# Create your models here.

class ReportTransactionPouch(models.Model):
    income = models.IntegerField(default=0)
    outcome = models.IntegerField(default=0)
    date_start = models.DateTimeField(auto_now=False, null=True)
    date_end = models.DateTimeField(auto_now=False, null=True)
    pouch = models.ForeignKey(Pouch, null=True)

class ReportTransactionPerson(models.Model):
    income = models.IntegerField(default=0)
    outcome = models.IntegerField(default=0)
    date_start = models.DateTimeField(auto_now=False, null=True)
    date_end = models.DateTimeField(auto_now=False, null=True)
    person = models.ForeignKey(Person, null=True)

class ReportTransactionCategory(models.Model):
    income = models.IntegerField(default=0)
    outcome = models.IntegerField(default=0)
    date_start = models.DateTimeField(auto_now=False, null=True)
    date_end = models.DateTimeField(auto_now=False, null=True)
    category = models.ForeignKey(Category, null=True)
