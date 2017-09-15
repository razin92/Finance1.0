from django.db import models
from lib.models import Person, Pouch, Category
from django.contrib.auth.models import User
from django.utils import timezone


class Transaction(models.Model):

    date = models.DateTimeField(verbose_name=(u'Время проведения'), default=timezone.now)
    sum_val = models.IntegerField(verbose_name=(u'Cумма'))
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name=(u'Категория'))
    who_is = models.ForeignKey(Person, on_delete=models.PROTECT, verbose_name=(u'На кого'))
    comment = models.CharField(max_length=50, blank=True, verbose_name=(u'Комментарий'))
    money = models.ForeignKey(Pouch, verbose_name=(u'Счет'))
    typeof = models.BooleanField(default=False, verbose_name=(u'Пополнение'))
    checking = models.BooleanField(default=True, verbose_name=(u'Проведено'))
    create_date = models.DateTimeField(default=timezone.now, verbose_name=(u'Дата создания/изменения'))
    creator = models.ForeignKey(User, default=User.objects.get(is_superuser=True).pk)

    def __unicode__(self):
        return self.date


