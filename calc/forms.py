from django import forms
from lib.models import Category, Person, Staff
from bootstrap3_datetime.widgets import DateTimePicker
from django.utils import timezone
import datetime

dnow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


class TransactionForm(forms.Form):
    error = {'required': ''}
    date = forms.DateTimeField(label="Дата*", widget=DateTimePicker(options={"format": "YYYY-MM-DD HH:mm"}), error_messages=error)
    sum_val = forms.IntegerField(label="Сумма*", max_value=999999999, min_value=1, error_messages=error)
    category = forms.ModelChoiceField(label="Категория*", queryset=Category.objects.all().order_by('name'), error_messages=error)
    who_is = forms.ModelChoiceField(label="От кого/кому*", queryset=Person.objects.all().order_by('firstname'), error_messages=error)
    money = forms.ModelChoiceField(label="Счет*", queryset=Staff.objects.none().order_by('name'), error_messages=error)
    comment = forms.CharField(label="Коммент", max_length=50, required=False)

    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user_id', None)
        super(TransactionForm, self).__init__(*args, **kwargs)
        self.fields['money'].queryset = Staff.objects.get(name__id=user_id).pouches.all()

class TranscationEdit:
    pass