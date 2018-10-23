from django.db import models
from salary.models import Worker

class Lib():

    def statuses(self):
        statuses_list = {
            ('1', 'Новая'),
            ('2', 'Принята мастером'),
            ('3', 'Закрыта мастером'),
            ('4', 'Закрыта'),
            ('5', 'Отменена'),
            ('6', 'Отказ мастера')
        }
        return statuses_list

    def results(self):
        results_list = {
            ('0', 'Неизвестная ошибка'),
            ('1', 'Успех'),
            ('2', 'Заявка не найдена'),
            ('3', 'Мастер не найден'),
            ('4', 'Неправильный статус'),
            ('5', 'Заявка уже существует')
        }
        return results_list

# Create your models here.
class SubscriberRequest(models.Model):

    def __init__(self, *args, **kwargs):
        super(SubscriberRequest, self).__init__(*args, **kwargs)
        self._meta.get_field('request_status').choices = Lib().statuses()

    request_id = models.CharField(default='0', max_length=9, unique=True)
    ref_key = models.CharField(max_length=50, unique=True)
    ops_date = models.DateTimeField(default=None, null=True, blank=True, auto_now=False)
    date = models.DateTimeField(auto_now=True)
    request_status = models.CharField(default='1', max_length=2)
    request_work = models.CharField(default='нет описания', max_length=100)
    request_address = models.CharField(default='q-b-a', max_length=50)
    worker = models.ForeignKey(Worker, null=True, blank=True)

    def __str__(self):
        displayed = '%s_%s_%s' % (
            self.request_id, self.request_work, self.request_status)
        return displayed

    def save(self, *args, **kwargs):
        result = kwargs.pop('result', '1')
        super(SubscriberRequest, self).save(*args, **kwargs)
        Logging().create_log(self, self.request_status, result)


class Logging(models.Model):

    def __init__(self, *args, **kwargs):
        super(Logging, self).__init__(*args, **kwargs)
        self._meta.get_field('request_status').choices = Lib().statuses()
        self._meta.get_field('request_result').choices = Lib().results()

    ops_date = models.DateTimeField(auto_now=True)
    request = models.ForeignKey(SubscriberRequest)
    request_status = models.CharField(default='1', max_length=2)
    request_result = models.CharField(default='1', max_length=2)

    def create_log(self, request, status, result):
        Logging.objects.create(
            request=request,
            request_status=status,
            request_result=result
        )