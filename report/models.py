from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from calc.models import Transaction
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

class TransactionChangeHistory(models.Model):
    transaction_id = models.IntegerField(blank=True, default=0)
    date_before = models.DateTimeField(blank=True)
    date_after = models.DateTimeField(blank=True, null=True)
    sum_val_before = models.IntegerField(blank=True, default=0)
    sum_val_after = models.IntegerField(blank=True, default=0)
    category_before = models.CharField(max_length=20, blank=True)
    category_after = models.CharField(max_length=20, blank=True)
    who_is_before = models.CharField(max_length=50, blank=True)
    who_is_after = models.CharField(max_length=50, blank=True)
    comment_before = models.CharField(max_length=50, blank=True)
    comment_after = models.CharField(max_length=50, blank=True)
    money_before = models.CharField(max_length=80, blank=True)
    money_after = models.CharField(max_length=80, blank=True)
    typeof_before = models.BooleanField(default=True)
    typeof_after = models.BooleanField(default=True)
    date_of_create = models.DateTimeField(blank=True)
    date_of_change = models.DateTimeField(blank=True)
    creator = models.CharField(max_length=150, blank=True)
    changer = models.CharField(max_length=150, blank=True)

class BalanceStamp(models.Model):
    date = models.DateTimeField(auto_now=True)
    pouch = models.ForeignKey(Pouch)
    sum_val = models.IntegerField(default=0)
    balance_before = models.IntegerField(default=0)
    balance_after = models.IntegerField(default=0)
    transaction = models.ForeignKey(Transaction, on_delete=models.PROTECT, null=True, blank=True)
    transaction_change = models.ForeignKey(TransactionChangeHistory, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.CharField(max_length=20)

    class Meta():
        ordering = ['date']


