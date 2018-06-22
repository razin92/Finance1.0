from django import forms
from django.contrib.auth.models import User
from django.forms.widgets import CheckboxSelectMultiple, HiddenInput
from .models import BonusWork, WorkCalc, Worker, CategoryOfChange, Work, WorkReport
from bootstrap3_datetime.widgets import DateTimePicker
import calendar
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

class WorkReportUserForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(WorkReportUserForm, self).__init__(*args, **kwargs)
        quarters = (
            (2, 2),
            (4, 4),
            (5, 5),
            (6, 6),
            (7, 7)
        )
        buildings = (
            ('', ''),
            ('А', 'А'),
            ('Б', 'Б'),
            ('В', 'В'),
        )
        self.fields['working_date'] = forms.DateField(
            label='Дата выполнения',
            initial=datetime.date.today(),
            widget=DateTimePicker(options={"format": "YYYY-MM-DD"})
        )
        self.fields['quarter'] = forms.ChoiceField(
            label='Квартал',
            choices=quarters,
        )
        self.fields['building'] = forms.ChoiceField(
            label='Дом',
            choices=self.generator(1, 110),
        )
        self.fields['building_litera'] = forms.ChoiceField(
            label='Буква дома',
            choices=buildings,
            required=False
        )
        self.fields['apartment'] = forms.ChoiceField(
            label='Квартира',
            choices=self.generator(1, 300),
            required=False,
        )
        self.fields['work'] = forms.ModelChoiceField(
            label='Работа',
            queryset=Work.objects.all().order_by('name')
        )
        self.fields['hours_qty'] = forms.ChoiceField(
            label='Затрачено часов',
            choices=self.generator(1, 25),
            initial=1,
        )
        self.fields['coworker'] = forms.MultipleChoiceField(
            label='Помощники',
            choices=((x.id, x.name) for x in Worker.objects.filter(
                position=WorkCalc.objects.filter(name='Мастер')
            )),
            widget=CheckboxSelectMultiple,
            required=False
        )
        self.fields['comment'] = forms.CharField(
            label='Комментарий',
	        max_length=1250,
            required=False,
            widget=forms.Textarea(
                attrs={
                    'rows': '4',
                }
            ),

        )

    def generator(self, start, stop):
        a = [(x, x) for x in range(start, stop)]
        b = [('', '')]
        result = tuple(b + a)
        return result

class WorkReportForm(forms.ModelForm):

    class Meta:
        model = WorkReport
        fields = ['working_date', 'quarter', 'building', 'apartment',
                  'work', 'hours_qty', 'coworker', 'comment', 'user']

    def __init__(self, *args, **kwargs):
        super(WorkReportForm, self).__init__(*args, **kwargs)
        self.fields['working_date'].widget = DateTimePicker(options={"format": "YYYY-MM-DD"})
        self.fields['comment'].widget = forms.Textarea(attrs={'rows': '4',})
        self.fields['user'].widget = HiddenInput()

class WorkForm(forms.ModelForm):

    class Meta:
        model = Work
        fields = ['name']

class MyWorkFilterForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(MyWorkFilterForm, self).__init__(*args, **kwargs)
        self.fields['date_start'].initial = self.today.replace(day=1)
        self.fields['date_end'].initial = self.today.replace(day=self.last_day)

    today = datetime.date.today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    confirmed_list = (
        ('True False', ''),
        ('True', 'Принята'),
        ('False', 'НЕ принята')
    )
    date_start = forms.DateField(
        label="Дата начала",
        widget=DateTimePicker(options={"format": "YYYY-MM-DD"})
    )
    date_end = forms.DateField(
        label="Дата окончания",
        widget=DateTimePicker(options={"format": "YYYY-MM-DD"})
    )
    '''
    work = forms.ModelChoiceField(
        Work.objects.all(),
        label="Работа",
        required=False
    )
    confirmed = forms.ChoiceField(
        choices=confirmed_list,
        label="Подтверждена",
        required=False
    )
    '''

class WorkFilterForm(forms.Form):

    working_date = forms.DateField(widget=DateTimePicker(options={"format": "YYYY-MM-DD"}))
    user = forms.ModelChoiceField(queryset=Worker.objects.filter(user__isnull=False))
    work = forms.ModelChoiceField(queryset=Work.objects.all())
    quarter = forms.ModelChoiceField(queryset=WorkReport.objects.all().values('quarter').distinct())

class ReportConfirmationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ReportConfirmationForm, self).__init__(*args, **kwargs)
        self.fields['cost'].required = False
        self.fields['admin_comment'].widget = forms.Textarea(attrs={'rows': '4'})
        self.fields['admin_comment'].required = False

    class Meta:
        model = WorkReport
        fields = ['cost', 'admin_comment']
