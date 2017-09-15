from django.db import models
from lib.models import Pouch, Person, Category

# Create your models here.

class ReportTransactionPouch(models.Model):
    income = models.CharField
    outcome = models.CharField
    date_start = models.DateTimeField
    date_end = models.DateTimeField
    pouch = models.ForeignKey(Pouch)

class ReportTransactionPerson(models.Model):
    income = models.CharField
    outcome = models.CharField
    date_start = models.DateTimeField
    date_end = models.DateTimeField
    person = models.ForeignKey(Person)

class ReportTransactionCategory(models.Model):
    income = models.CharField
    outcome = models.CharField
    date_start = models.DateTimeField
    date_end = models.DateTimeField
    category = models.ForeignKey(Category)
