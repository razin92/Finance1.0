from django import forms
from salary.models import Worker, WorkCalc, BonusWork, Total, AccountChange
from lib.models import Person, Staff, Category
from bootstrap3_datetime.widgets import DateTimePicker
from django.forms.widgets import CheckboxSelectMultiple
import datetime


dnow = datetime.datetime.now()
date_begin = datetime.datetime(dnow.year, dnow.month, 1).strftime('%Y-%m-%d')
date_end = datetime.datetime(dnow.year, dnow.month, dnow.day, hour=23, minute=59).strftime('%Y-%m-%d')


class WorkerFilter(forms.Form):
    date_start = forms.DateField(
        label = "Начало периода",
        widget = DateTimePicker(options={"format": "YYYY-MM-DD"}),
        initial = date_begin
    )
    date_end = forms.DateField(
        label = "Конец периода",
        widget = DateTimePicker(options={"format": "YYYY-MM-DD"}),
        initial = date_end
    )
    worker = forms.ModelMultipleChoiceField(
        label = "Работники",
        queryset = Worker.objects.all().order_by('name'),
        widget = CheckboxSelectMultiple
    )

class TransactionFilterForm(forms.Form):
    who_is = forms.MultipleChoiceField(
        label = "Персона",
        choices = ((element.firstname, element) for element in Person.objects.all().order_by('firstname')),
        widget = CheckboxSelectMultiple
    )
    money = forms.MultipleChoiceField(
        label = "Счета",
        choices = (),
        widget = CheckboxSelectMultiple,
    )
    category = forms.MultipleChoiceField(
        label = "Категории",
        choices = ((element.name, element) for element in Category.objects.all().order_by('name')),
        widget = CheckboxSelectMultiple
    )
    comment = forms.CharField(
        label = "Комментарии"
    )

    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user_id', None)
        super(TransactionFilterForm, self).__init__(*args, **kwargs)
        self.fields['money'].choices = ((element.name, element) for element in Staff.objects.get(name__id=user_id).pouches.all().order_by('name'))