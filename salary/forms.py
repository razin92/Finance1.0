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

class MassBonusForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(MassBonusForm, self).__init__(*args, **kwargs)
        self.fields['workers'].queryset = Worker.objects.filter(fired=False).order_by('name__firstname')

    date = forms.DateField(label="Дата", initial=datetime.date.today(),
                           widget=DateTimePicker(options={"format": "YYYY-MM-DD"}))
    model = forms.ModelChoiceField(label="Работа", queryset=WorkCalc.objects.all().order_by('name'))
    quantity = forms.IntegerField(label="Кол-во", min_value=1, max_value=100, initial=1)
    comment = forms.CharField(label="Комментарий", max_length=100, required=False)
    workers = forms.ModelMultipleChoiceField(
        label="Работники",
        widget=CheckboxSelectMultiple,
        queryset=None)

class AccountChangeForm(forms.Form):
    date = forms.DateField(label="Дата", initial=datetime.date.today(), widget=DateTimePicker(options={"format": "YYYY-MM-DD"}))
    summ = forms.IntegerField(label="Сумма", initial=5000)
    worker = forms.ModelChoiceField(label="Работник", queryset=Worker.objects.all().order_by('name__firstname'))
    reason = forms.ModelChoiceField(label="Основание", queryset=CategoryOfChange.objects.all().order_by('name'))
    comment = forms.CharField(label="Комментарий", max_length=100, required=False)
    withholding = forms.BooleanField(label="Удержание", required=False)

class WorkReportUserForm(forms.Form):

    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user_id', None)
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
        '''
        self.fields['working_date'] = forms.DateField(
            label='Дата выполнения',
            initial=datetime.date.today(),
            widget=DateTimePicker(options={"format": "YYYY-MM-DD"})
        )
        '''
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
                can_make_report=True).exclude(user__id=user_id)),
            widget=CheckboxSelectMultiple,
            required=False
        )
        self.fields['income'] = forms.IntegerField(
            label='Принятые кредиты',
            initial=None
        )
        self.fields['comment'] = forms.CharField(
            label='Комментарий',
            max_length=255,
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


class WorkReportTaggedForm(forms.Form):

    def __init__(self, *args, **kwargs):
        work = kwargs.pop('work', None)
        user = kwargs.pop('user_id', None)
        super(WorkReportTaggedForm, self).__init__()
        self.fields['mock_working_date'] = forms.DateField(
            label='Дата выполнения',
            disabled=True,
            initial=work.working_date,
        )
        self.fields['working_date'] = forms.DateField(
            widget=HiddenInput,
            initial=work.working_date,
        )
        self.fields['mock_quarter'] = forms.CharField(
            label='Квартал',
            disabled=True,
            initial=work.quarter,
        )
        self.fields['quarter'] = forms.CharField(
            widget=HiddenInput,
            initial=work.quarter,
        )
        self.fields['mock_building'] = forms.CharField(
            label='Дом',
            disabled=True,
            initial=work.building,
        )
        self.fields['building'] = forms.CharField(
            widget=HiddenInput,
            initial=work.building,
        )
        self.fields['building_litera'] = forms.CharField(
            initial='',
            widget=HiddenInput
        )
        self.fields['mock_apartment'] = forms.CharField(
            label='Квартира',
            disabled=True,
            initial=work.apartment,
        )
        self.fields['apartment'] = forms.CharField(
            widget=HiddenInput,
            initial=work.apartment,
        )
        self.fields['mock_work'] = forms.CharField(
            label='Работа',
            disabled=True,
            initial=work.work
        )
        self.fields['work'] = forms.CharField(
            widget=HiddenInput,
            initial=work.work.id
        )
        self.fields['mock_hours_qty'] = forms.CharField(
            label='Затрачено часов',
            disabled=True,
            initial=work.hours_qty,
        )
        self.fields['hours_qty'] = forms.CharField(
            widget=HiddenInput,
            initial=work.hours_qty,
        )
        self.fields['coworkers'] = forms.CharField(
            label='Участники этой работы',
            disabled=True,
            initial=', '.join(['%s' % x for x in Worker.objects.filter(
                id__in=[x.id for x in work.coworker.all()])]) + ', %s' % Worker.objects.get(user=work.user)
        )
        self.fields['coworker'] = forms.MultipleChoiceField(
            label='Помощники',
            choices=((x.id, x.name) for x in Worker.objects.filter(
                can_make_report=True).exclude(user__id=user)),
            initial=self.get_worker(work, user),
            widget=CheckboxSelectMultiple,
            required=False
        )
        self.fields['comment'] = forms.CharField(
            label='Комментарий',
            max_length=255,
            required=False,
            initial=work.comment,
            widget=forms.Textarea(
                attrs={
                    'rows': '4',
                }
            ),

        )
        self.fields['new'] = forms.BooleanField(
            initial=True,
            widget=HiddenInput
        )

    def get_worker(self, work, user):
        result = [x.id for x in Worker.objects.filter(
            id__in=[x.id for x in work.coworker.all().exclude(user__id=user)])
                  ]
        result.append(Worker.objects.get(user=work.user).id)
        return result

class WorkReportForm(forms.ModelForm):

    class Meta:
        model = WorkReport
        fields = ['working_date', 'quarter', 'building', 'apartment',
                  'work', 'hours_qty', 'coworker', 'income', 'comment', 'user']

    def __init__(self, *args, **kwargs):
        super(WorkReportForm, self).__init__(*args, **kwargs)
        self.fields['working_date'].widget = DateTimePicker(options={"format": "YYYY-MM-DD"})
        self.fields['comment'].widget = forms.Textarea(attrs={'rows': '4',})
        self.fields['user'].widget = HiddenInput()
        self.fields['coworker'].queryset = Worker.objects.filter(
            can_make_report=True).exclude(user__id=kwargs['instance'].user.id)
        self.fields['income'].initial = None

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

    def __init__(self, *args, **kwargs):
        super(WorkFilterForm, self).__init__(*args, **kwargs)
        self.fields['working_date_start'].initial = datetime.date.today().replace(day=1)
        self.fields['working_date_end'].initial = datetime.date.today()

    do_not_use_date = forms.BooleanField(
        label="Не учитывать дату",
        required=False,
        initial=False
    )
    working_date_start = forms.DateField(
        widget=DateTimePicker(options={"format": "YYYY-MM-DD"}),
        required=False,
        label="Начало периода"
    )
    working_date_end = forms.DateField(
        widget=DateTimePicker(options={"format": "YYYY-MM-DD"}),
        required=False,
        label="Конец периода"
    )
    workers = forms.ModelMultipleChoiceField(
        queryset=Worker.objects.filter(can_make_report=True),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Работники"
    )
    work = forms.ModelMultipleChoiceField(
        queryset=Work.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Работа"
    )
    quarter = forms.IntegerField(
        required=False,
        label="Квартал",
    )
    building = forms.CharField(
        required=False,
        label="Дом",
    )
    apartment = forms.IntegerField(
        required=False,
        label="Квартира",
    )

class ReportConfirmationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ReportConfirmationForm, self).__init__(*args, **kwargs)
        self.fields['cost'].initial = None
        self.fields['cost'].required = False
        self.fields['admin_comment'].widget = forms.Textarea(
            attrs={'rows': '4', 'maxlength': '255'})
        self.fields['admin_comment'].required = False

    class Meta:
        model = WorkReport
        fields = ['cost', 'admin_comment']
