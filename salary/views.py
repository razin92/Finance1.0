from django.views.generic import View, ListView, CreateView, UpdateView
from .models import Worker, WorkCalc, BonusWork, AccountChange, CategoryOfChange, Total, WorkReport, Work
from calc.models import Transaction
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from .forms import BonusWorkForm, AccountChangeForm, \
    WorkReportUserForm, WorkForm, WorkFilterForm, MyWorkFilterForm, \
    ReportConfirmationForm
from calc.forms import MonthForm
from django.db.models import Count
import datetime
import calendar
import time
# Create your views here.
global code


class WorkerView(ListView):
    template_name = 'salary/worker_list.html'
    context_object_name = 'worker'

    def get_queryset(self):
        return Worker.objects.order_by('name__firstname')

class WorkerCreate(CreateView):
    model = Worker
    success_url = reverse_lazy('salary:worker')
    fields = ['name', 'position', 'category']
    template_name = 'salary/worker_create.html'


class WorkCalcView(ListView):
    template_name = 'salary/workcalc_list.html'
    context_object_name = 'workcalc'

    def get_queryset(self):
        return WorkCalc.objects.order_by('name')


class WorkCalcCreate(CreateView):
    model = WorkCalc
    success_url = reverse_lazy('salary:workcalc')
    fields = ['name', 'time_range', 'cost']
    template_name = 'salary/workcalc_create.html'


class BonusWorkView(ListView):
    template_name = 'salary/bonuswork_list.html'
    context_object_name = 'bonuswork'

    def get_queryset(self):
        return BonusWork.objects.order_by('-date')


def BonusWorkCreate(request):
    form = BonusWorkForm(request.POST or None)
    user = request.user
    template = 'salary/bonuswork_create.html'
    context = {
        'form': form,
        'user': user
    }
    if request.method == 'POST' and form.is_valid():
        BonusWork.objects.create(**form.cleaned_data)
        return HttpResponseRedirect(reverse('salary:bonuswork'))
    else:
        return render(request, template, context)

class BonusWorkEdit(UpdateView):
    model = BonusWork
    template_name = 'salary/bonuswork_edit.html'
    success_url = reverse_lazy('salary:bonuswork')
    fields = ['date', 'model', 'worker', 'quantity', 'comment']


class AccountChangeView(ListView):
    template_name = 'salary/accountchange_list.html'
    context_object_name = 'accountchange'

    def get_queryset(self):
        return AccountChange.objects.order_by('-date')

def AccountChangeCreate(request):
    form = AccountChangeForm(request.POST or None)
    user = request.user
    template = 'salary/accountchange_create.html'
    context = {
        'form': form,
        'user': user
    }

    if request.method == 'POST' and form.is_valid():
        AccountChange.objects.create(**form.cleaned_data)
        return HttpResponseRedirect(reverse('salary:accountchange'))
    else:
        return render(request, template, context)

class AccountChangeEdit(UpdateView):
    model = AccountChange
    template_name = 'salary/accountchange_edit.html'
    success_url = reverse_lazy('salary:accountchange')
    fields = ['date', 'summ', 'worker', 'reason', 'comment']

class CategoryOfChangeView(ListView):
    template_name = 'salary/categoryofchange_list.html'
    context_object_name = 'categoryofchange'

    def get_queryset(self):
        return CategoryOfChange.objects.order_by('name')


class CategoryOfChangeCreate(CreateView):
    model = CategoryOfChange
    success_url = reverse_lazy('salary:categoryofchange')
    fields = ['name']
    template_name = 'salary/categoryofchange_create.html'


def TotalView(request):
    rqst = request.POST
    if 'select_month' in rqst and rqst['select_month']:
        date = rqst['select_month']
    else:
        date = str(timezone.now().month)
    def get_queryset(date):
        total = Total.objects.filter(date__month=date)
        return total.all().order_by('worker__name')
    user = request.user
    form = MonthForm
    template = 'salary/total_list.html'
    context = {
        'total': get_queryset(date),
        'user': user,
        'form': form,
    }
    return render(request, template, context)

def TotalCreate(request):
    workers = Worker.objects.all()
    total = Total.objects.filter(date__month=datetime.datetime.now().month)
    total_workers = [each.worker for each in total.all()]
    month_now = datetime.datetime.now().replace(day=1)

    for each in workers:
        if each not in total_workers:
            Total.objects.create(worker=each, date=month_now)

    return HttpResponseRedirect(reverse('salary:calculate', args={'2': '2'}))

@login_required()
def accrual(request, worker_id):
    worker = get_object_or_404(Worker, pk=worker_id)
    work = worker.position.all()
    return render(request, 'salary/total_work_detail.html',{
                  'work': work,
                  'worker': worker
    }
                  )

@login_required()
def bonus(request, worker_id, total_id):
    worker = get_object_or_404(Worker, pk=worker_id)
    total = Total.objects.get(pk=total_id)
    month = total.date.month
    last_month = month - 1
    last_year = total.date.year
    if last_month == 0:
        last_month = 12
        last_year -= 1

    correction = AccountChange.objects.filter(
        worker=worker,
        date__month=last_month,
        date__year=last_year,
        withholding=False,
        checking=True
    ).order_by('-date')
    bonus = BonusWork.objects.filter(
        worker=worker,
        date__month=last_month,
        date__year=last_year,
        withholding=False,
        checking=True
    ).order_by('-date')
    return render(request, 'salary/total_bonus_detail.html', {
        'worker': worker,
        'bonus': bonus,
        'correction': correction
    }
                )

@login_required()
def withholding(request, worker_id, total_id):
    worker = get_object_or_404(Worker, pk=worker_id)
    total = Total.objects.get(pk=total_id)
    month = total.date.month
    last_month = month - 1
    last_year = total.date.year
    if last_month == 0:
        last_month = 12
        last_year -= 1

    correction = AccountChange.objects.filter(
        worker=worker,
        date__month=last_month,
        date__year=last_year,
        withholding=True,
        checking=True
    ).order_by('-date')
    bonus = BonusWork.objects.filter(
        worker=worker,
        date__month=last_month,
        date__year=last_year,
        withholding=True,
        checking=True
    ).order_by('-date')
    return render(request, 'salary/total_withholding_detail.html', {
        'worker': worker,
        'bonus': bonus,
        'correction': correction
    }
                  )

@login_required()
def issued(request, worker_id, total_id):
    worker = get_object_or_404(Worker, pk=worker_id)
    total = Total.objects.get(pk=total_id)
    month = total.date.month
    next_year = total.date.year
    next_month = month + 1
    if next_month == 13:
        next_month = 1
        next_year += 1
    year = Total.objects.get(pk=total_id).date.year
    issued = Transaction.objects.filter(
        who_is=worker.name,
        category=worker.category,
        date__range=(
            datetime.datetime(year, month, 1),
            datetime.datetime(next_year, next_month, 1)
        ),
        checking=True
    ).order_by('-date')
    return render(request, 'salary/total_issued_detail.html', {
        'worker': worker,
        'issued': issued
    })

@login_required()
def calculate(request, code):
    total_list = Total.objects.filter(date__month=timezone.now().month)
    date = {'month': timezone.now().month, 'year': timezone.now().year}
    for total in total_list:
        total.balance_before_calc(date=date)
        total.accrual_calc(date=date)
        total.bonus_calc(date=date)
        total.withholding_calc(date=date)
        total.balance_after_calc(date=date)
        total.issued_calc(date=date)
        total.balance_now_calc(date=date)
    if code == '1':
        return HttpResponseRedirect(reverse('salary:worker'))
    elif code == '2':
        return HttpResponseRedirect(reverse('salary:total'))

@login_required()
def get_salary(request):
    for each in Worker.objects.all():
        each.get_salary()
    return HttpResponseRedirect(reverse('salary:calculate', args={'2': '2'}))

class WorkerReportUser(View):
    template = 'salary/work_report.html'

    def get(self, request):
        form = WorkReportUserForm(None)
        context = {
            'form': form,
        }
        return render(request, self.template, context)

    def post(self, request):
        form = WorkReportUserForm(request.POST)
        context = {
            'form': form,
        }
        if form.is_valid():
            new_object = self.WorkReportCreate(form.data, request.user)
            coworkers = request.POST.getlist('coworker', '')
            for x in coworkers:
                new_object.coworker.add(x)
        return render(request, self.template, context)

    def WorkReportCreate(self, data, user):
        result = WorkReport.objects.create(
            working_date=data['working_date'],
            hours_qty=data['hours_qty'],
            user=user,
            work=Work.objects.get(pk=data['work']),
            quarter=data['quarter'],
            building='%s%s' % (data['building'], data['building_litera']),
            apartment=data['apartment'],
            comment=self.get_parameter(data, 'comment')
        )
        result.save()
        return result

    def get_parameter(self, data, name):
        if name in data:
            return data[name]
        return ''

class WorkView(View):
    template = 'salary/work_report.html'

    def get(self, request):
        form = WorkForm(None)
        context = {
            'form': form,
        }
        return render(request, self.template, context)

    def post(self, request):
        form = WorkForm(request.POST)
        context = {
            'form': form,
        }
        if form.is_valid():
            form.save()
        return render(request, self.template, context)

class MyWorkList(View):
    template = 'salary/work_list.html'
    today = datetime.date.today()
    last_day = calendar.monthcalendar(today.year, today.month)[1]

    def get(self, request, page):
        form = MyWorkFilterForm(request.POST or None)
        data = WorkReport.objects.filter(
            user=request.user,
            working_date__month=self.today.month
        ).order_by('-working_date')
        #summ = data.values('cost').aggregate(('cost'))
        exclude_list = ['filling_date', 'user']
        header = [x for x in WorkReport._meta.get_fields() if x.name not in exclude_list]
        splitter = Paginator(data, 25)
        split_data = splitter.page(page)
        context = {
            'header': header,
            'data': split_data.object_list,
            'pages': split_data,
            'form': form
        }
        return render(request, self.template, context)

    def post(self, request):
        form = MyWorkFilterForm(request.POST or None)
        start = request.POST['date_start']
        end = request.POST['date_end']
        data = WorkReport.objects.filter(
            user=request.user,
            working_date__range=(start, end)
        ).order_by('-working_date')
        exclude_list = ['filling_date', 'user']
        header = [x for x in WorkReport._meta.get_fields() if x.name not in exclude_list]
        context = {
            'header': header,
            'data': data,
            'form': form
        }
        return render(request, self.template, context)

class ReportsList(View):
    template = 'salary/work_reports_list.html'

    def get(self, request):
        page = request.GET.get('page') or 1
        dupes = self.get_duplicate(WorkReport)
        data = WorkReport.objects.all().order_by('working_date', 'user')
        data_per_page = Paginator(data, 25)
        result = data_per_page.page(page)
        exclude_list = ['filling_date']
        header = [x for x in WorkReport._meta.get_fields() if x.name not in exclude_list]
        context = {
            'header': header,
            'data': result.object_list,
            'pages': result,
            'dupes': dupes
        }
        return render(request, self.template, context)


    def get_duplicate(self, data):

        duplicates = data.objects.values('quarter', 'building', 'apartment')\
            .annotate(Count('quarter'), Count('building'), Count('apartment'))\
            .order_by()\
            .filter(
            building__count__gt=1,
            quarter__count__gt=1,
            apartment__count__gt=1
        )

        dupl = WorkReport.objects.filter(
            quarter__in=[x['quarter'] for x in duplicates],
            building__in=[x['building'] for x in duplicates],
            apartment__in=[x['apartment'] for x in duplicates],
        ).order_by('building')

        return dupl

class ReportConfirmation(View):
    template = 'salary/report_confirmation.html'

    def get(self, request):
        rqst = request.GET
        form = ReportConfirmationForm(rqst or None)
        data, result = '', ''
        if request.user.has_perm('salary.change_workreport'):
            if 'id' in rqst and 'cost' in rqst:
                result = self.update_report(rqst['id'], rqst['cost'])
            if 'deleted' in rqst:
                result = self.update_report(rqst['id'],deleted=True)
            data = WorkReport.objects.filter(confirmed=False).order_by(
            '-working_date', 'user').distinct()
        if data.__len__() > 0:
            data = data[0]
        context = {
            'data': data,
            'form': form,
            'result': result,
        }
        return render(request, self.template, context)

    def update_report(self, id, cost=0, deleted=False):
        data = WorkReport.objects.get(id=id)
        data.cost = cost
        data.confirmed = True
        data.deleted = deleted
        data.save()
        message = 'Отчет №%s, выполненный %s подтвержден' % (id, data.user)
        print('%s - Confirmed %s report with cost %s by %s' % (timezone.now(),id, cost, self.request.user))
        if deleted:
            message = 'Отчет №%s, выполненный %s удален' % (id, data.user)
        return message