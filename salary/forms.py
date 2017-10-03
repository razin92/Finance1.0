from django import forms
from .models import BonusWork, WorkCalc, Worker, CategoryOfChange
from bootstrap3_datetime.widgets import DateTimePicker
import datetime

class BonusWorkForm(forms.Form):
    date = forms.DateField(label="Дата", initial=datetime.date.today(), widget=DateTimePicker(options={"format": "YYYY-MM-DD"}))
    model = forms.ModelChoiceField(label="Работа", queryset=WorkCalc.objects.all().order_by('name'))
    worker = forms.ModelChoiceField(label="Работник", queryset=Worker.objects.all().order_by('name__firstname'))
    quantity = forms.IntegerField(label="Кол-во", min_value=1, max_value=100, initial=1)
    comment = forms.CharField(label="Комментарий", max_length=100, required=False)
    withholding = forms.BooleanField(label="Удержание", required=False)

class AccountChangeForm(forms.Form):
    date = forms.DateField(label="Дата", initial=datetime.date.today(), widget=DateTimePicker(options={"format": "YYYY-MM-DD"}))
    summ = forms.IntegerField(label="Сумма", initial=5000)
    worker = forms.ModelChoiceField(label="Работник", queryset=Worker.objects.all().order_by('name__firstname'))
    reason = forms.ModelChoiceField(label="Основание", queryset=CategoryOfChange.objects.all().order_by('name'))
    comment = forms.CharField(label="Комментарий", max_length=100, required=False)
    withholding = forms.BooleanField(label="Удержание", required=False)