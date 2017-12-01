from django.db import models
from django.utils import timezone
from lib.models import Person, Category
from django.contrib.auth.models import User
from calc.models import Transaction
import datetime
#Должность

class WorkCalc(models.Model):
    time = {
        ('Час','hour'),
        ('День', 'day'),
        ('Месяц', 'month'),
        ('Процент', 'percent'),
        ('Оклад', 'salary')
    }
    name = models.CharField(max_length=20)
    time_range = models.CharField(max_length=20, choices=time)
    cost = models.IntegerField(default=0)

    def __str__(self):
        return self.name

class Worker(models.Model):
    name = models.OneToOneField(Person)
    account = models.IntegerField(default=0)
    position = models.ManyToManyField(WorkCalc)
    category = models.ForeignKey(Category, null=True)

    def __str__(self):
        return str(self.name)

class BonusWork(models.Model):
    model = models.ForeignKey(WorkCalc)
    worker = models.ForeignKey(Worker, null=True)
    quantity = models.IntegerField(default=1)
    date = models.DateField(default=timezone.now)
    comment = models.CharField(max_length=100, blank=True)
    checking = models.BooleanField(default=True)
    withholding = models.BooleanField(default=False)

    def __str__(self):
        return str(self.model)

    def calculate(self):
        result = BonusWork.objects.get(pk=self.id)
        calc = result.model.cost * result.quantity
        return calc

class CategoryOfChange(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class AccountChange(models.Model):
    summ = models.IntegerField(default=0)
    reason = models.ForeignKey(CategoryOfChange)
    worker = models.ForeignKey(Worker)
    date = models.DateField(default=timezone.now)
    comment = models.CharField(max_length=100, blank=True)
    checking = models.BooleanField(default=True)
    withholding = models.BooleanField(default=False)
    responsible = models.CharField(max_length=20, default='user')

    def __str__(self):
        return str(self.summ) + ' ' + str(self.worker) + ' ' + str(self.date)

class Total(models.Model):
    date = models.DateField(default=timezone.now().replace(day=1))
    worker = models.ForeignKey(Worker)
    balance_before = models.IntegerField(default=0)
    accrual = models.IntegerField(default=0)
    bonus = models.IntegerField(default=0)
    withholding = models.IntegerField(default=0)
    balance_after = models.IntegerField(default=0)
    issued = models.IntegerField(default=0)
    balance_now = models.IntegerField(default=0)

    class Meta():
        unique_together = ('date', 'worker')

    def __str__(self):
        return str(self.date) + ' ' + str(self.worker)

    def balance_before_calc(self):
        total = Total.objects.get(worker=self.worker, date__month=timezone.now().month)
        try:
            total.balance_before = Total.objects.get(worker=self.worker, date__month=total.date.month-1).balance_now
            total.save()
        except:
            return "Error"

    def accrual_calc(self):
        total = Total.objects.get(worker=self.worker, date__month=timezone.now().month)
        total.accrual = 0
        for x in total.worker.position.all():
            total.accrual += x.cost
        total.save()

    def bonus_calc(self):
        total = Total.objects.get(worker=self.worker, date__month=timezone.now().month)
        bonus = BonusWork.objects.filter(
            worker=total.worker,
            date__month=total.date.month-1,
            withholding=False,
            checking=True
        )
        correction = AccountChange.objects.filter(
            worker=total.worker,
            date__month=total.date.month-1,
            withholding=False,
            checking=True
        )
        total.bonus = 0
        for each in bonus.all():
            total.bonus += each.calculate()

        for each in correction.all():
            total.bonus += each.summ

        total.save()


    def withholding_calc(self):
        total = Total.objects.get(worker=self.worker, date__month=timezone.now().month)
        bonus = BonusWork.objects.filter(
            worker=total.worker,
            date__month=total.date.month - 1,
            withholding=True,
            checking=True
        )
        correction = AccountChange.objects.filter(
            worker=total.worker,
            date__month=total.date.month - 1,
            withholding=True,
            checking=True
        )
        total.withholding = 0
        for each in bonus.all():
            total.withholding += each.calculate()

        for each in correction.all():
            total.withholding += each.summ

        total.save()


    def balance_after_calc(self):
        total = Total.objects.get(worker=self.worker, date__month=timezone.now().month)
        total.balance_after = 0
        total.balance_after = total.balance_before + total.accrual + total.bonus - total.withholding
        total.save()


    def issued_calc(self):
        total = Total.objects.get(worker=self.worker, date__month=timezone.now().month)
        year = total.date.year
        month = total.date.month
        next_month = month + 1
        if month + 1 == 13:
            next_month = 1
        issued = Transaction.objects.filter(
            who_is=total.worker.name,
            category=total.worker.category,
            date__range=(
                datetime.datetime(year, month, 1),
                datetime.datetime(year, next_month, 1)
            ),
            checking=True
        )
        total.issued = 0
        for x in issued.all():
            if x.typeof:
                total.issued -= x.sum_val
            else:
                total.issued += x.sum_val
        total.save()

    def balance_now_calc(self):
        total = Total.objects.get(worker=self.worker, date__month=timezone.now().month)
        worker = Worker.objects.get(name=total.worker.name)
        worker.account = 0
        total.balance_now = 0
        total.balance_now = total.balance_after - total.issued
        worker.account = total.balance_now
        worker.save()
        total.save()