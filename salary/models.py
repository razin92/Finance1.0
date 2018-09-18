from django.db import models
from django.utils import timezone
from lib.models import Person, Category, Pouch
from django.contrib.auth.models import User
from calc.models import Transaction
from django.core.exceptions import ObjectDoesNotExist
import datetime


# Должность
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
    salary = models.IntegerField(default=650000)
    user = models.OneToOneField(User, null=True, blank=True)
    can_make_report = models.BooleanField(default=False)
    fired = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)

    def get_salary(self):
        date_today = timezone.now().replace(day=1, hour=15, minute=00, second=00, microsecond=000000)
        account, created = Pouch.objects.get_or_create(
            name='System',
            defaults={'balance': 0},
        )
        Transaction.objects.get_or_create(
            date=date_today,
            sum_val=self.salary,
            category=self.category,
            who_is=self.name,
            money=account
        )
        return date_today


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

    def object_filter(self, date):
        total = Total.objects.get(
            worker=self.worker,
            date__month=date['month'],
            date__year=date['year'],
        )
        return total

    def balance_before_calc(self, date):
        total = self.object_filter(date=date)
        last_month = total.date.month - 1
        last_year = date['year']
        if total.date.month == 1:
            last_month = 12
            last_year = date['year'] - 1
        try:
            total.balance_before = Total.objects.get(
                worker=self.worker,
                date__month=last_month,
                date__year=last_year
            ).balance_now
            total.save()
        except:
            return "Error"

    def accrual_calc(self, date):
        total = self.object_filter(date=date)
        total.accrual = 0
        for x in total.worker.position.all():
            total.accrual += x.cost
        total.save()

    def bonus_calc(self, date):
        total = self.object_filter(date=date)
        last_month = total.date.month - 1
        last_year = date['year']
        if total.date.month == 1:
            last_month = 12
            last_year = date['year'] - 1
        bonus = BonusWork.objects.filter(
            worker=total.worker,
            date__month=last_month,
            date__year=last_year,
            withholding=False,
            checking=True
        )
        correction = AccountChange.objects.filter(
            worker=total.worker,
            date__month=last_month,
            date__year=last_year,
            withholding=False,
            checking=True
        )
        total.bonus = 0
        for each in bonus.all():
            total.bonus += each.calculate()

        for each in correction.all():
            total.bonus += each.summ
        total.save()

    def withholding_calc(self, date):
        total = self.object_filter(date=date)
        last_month = total.date.month - 1
        last_year = date['year']
        if total.date.month == 1:
            last_month = 12
            last_year = date['year'] - 1

        bonus = BonusWork.objects.filter(
            worker=total.worker,
            date__month=last_month,
            date__year=last_year,
            withholding=True,
            checking=True
        )
        correction = AccountChange.objects.filter(
            worker=total.worker,
            date__month=last_month,
            date__year=last_year,
            withholding=True,
            checking=True
        )
        total.withholding = 0
        for each in bonus.all():
            total.withholding += each.calculate()

        for each in correction.all():
            total.withholding += each.summ
        total.save()

    def balance_after_calc(self, date):
        total = self.object_filter(date=date)
        total.balance_after = 0
        total.balance_after = total.balance_before + total.accrual + total.bonus - total.withholding
        total.save()

    def issued_calc(self, date):
        total = self.object_filter(date=date)
        last_year = total.date.year
        next_year = last_year
        month = total.date.month
        next_month = month + 1
        if next_month == 13:
            next_month = 1
            next_year += 1
        issued = Transaction.objects.filter(
            who_is=total.worker.name,
            category=total.worker.category,
            date__range=(
                datetime.datetime(last_year, month, 1),
                datetime.datetime(next_year, next_month, 1)
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

    def balance_now_calc(self, date):
        total = self.object_filter(date=date)
        worker = Worker.objects.get(name=total.worker.name)
        worker.account = 0
        total.balance_now = 0
        total.balance_now = total.balance_after - total.issued
        worker.account = total.balance_now
        worker.save()
        total.save()

    def calculate(self, date):
        self.balance_before_calc(date=date)
        self.accrual_calc(date=date)
        self.bonus_calc(date=date)
        self.withholding_calc(date=date)
        self.balance_after_calc(date=date)
        self.issued_calc(date=date)
        self.balance_now_calc(date=date)


class Work(models.Model):
    name = models.CharField(max_length=50, verbose_name="Вид работ", unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class WorkReport(models.Model):
    filling_date = models.DateField(auto_now=True, verbose_name="Дата заполнения")
    working_date = models.DateField(verbose_name="Дата")
    hours_qty = models.SmallIntegerField(default=1, verbose_name="Часы")
    user = models.ForeignKey(User, verbose_name="Ответственный")
    work = models.ForeignKey(Work, verbose_name="Вид работ")
    coworker = models.ManyToManyField(Worker, blank=True, verbose_name="Помощники")
    quarter = models.SmallIntegerField(verbose_name="Кв-л")
    building = models.CharField(max_length=4, verbose_name="Дом")
    apartment = models.SmallIntegerField(null=True, blank=True, verbose_name="Кв-ра")
    confirmed = models.BooleanField(default=False, verbose_name="Принята")
    cost = models.IntegerField(default=None, verbose_name="Стоимость", null=True)
    income = models.IntegerField(default=None, null=True, verbose_name="Принятые кредиты", blank=True)
    comment = models.CharField(max_length=255, blank=True, null=True, verbose_name="Комментарий")
    admin_comment = models.CharField(max_length=255, blank=True, verbose_name="Комментарий начальника")
    deleted = models.BooleanField(default=False, verbose_name="Удален")
    tagged_coworker = models.BooleanField(default=False, verbose_name="Отмечен помощник")
    coworkers_qt_ty = models.SmallIntegerField(default=1, verbose_name="Кол-во подтвержденных")
    stored = models.BooleanField(default=False, verbose_name="Отложен")
    transaction = models.OneToOneField(Transaction, null=True, blank=True, verbose_name="Связанная транзакция")

    def __str__(self):
        return '%s %s %s' % (self.working_date, self.work, self.user)

    class Meta:
        unique_together = ['working_date', 'work', 'user', 'quarter', 'building', 'apartment', 'comment']
        ordering = ['-working_date']

    def tag_coworker(self):
        if self.coworker is not None:
            self.tagged_coworker = True
            self.save()

    def untag_coworker(self):
        if self.coworker.all().__len__() <= self.coworkers_qt_ty:
            self.tagged_coworker = False
            self.save()
        else:
            self.c_counter()

    def store_work(self):
        self.stored = True
        self.save()

    def c_counter(self):
        self.coworkers_qt_ty += 1
        self.save()

    def check_report(self, user):
        try:
            work = WorkReport.objects.get(
                working_date=self.working_date,
                quarter=self.quarter,
                building=self.building,
                apartment=self.apartment,
                user=user,
                work=self.work,
            )
            if work:
                return False
        except ObjectDoesNotExist:
            return True

