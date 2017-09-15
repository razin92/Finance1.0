from django import forms
from salary.models import Worker, WorkCalc, BonusWork, Total, AccountChange
from bootstrap3_datetime.widgets import DateTimePicker
from django.forms.widgets import CheckboxSelectMultiple
import datetime


dnow = datetime.datetime.now()
date_begin = datetime.datetime(dnow.year, dnow.month, 1).strftime('%Y-%m-%d')
date_end = datetime.datetime(dnow.year, dnow.month, dnow.day, hour=23, minute=59).strftime('%Y-%m-%d')


class WorkerFilter(forms.Form):
    date_start = forms.DateField(label="Начало периода", widget=DateTimePicker(options={"format": "YYYY-MM-DD"}), initial=date_begin)
    date_end = forms.DateField(label="Конец периода", widget=DateTimePicker(options={"format": "YYYY-MM-DD"}), initial=date_end)
    worker = forms.ModelMultipleChoiceField(label="Работники", queryset=Worker.objects.all().order_by('name'), widget=CheckboxSelectMultiple)

