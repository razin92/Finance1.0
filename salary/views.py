from django.views import generic
from .models import Worker, WorkCalc, BonusWork, AccountChange, CategoryOfChange, Total
from calc.models import Transaction
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy, reverse
from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import BonusWorkForm, AccountChangeForm
import datetime
# Create your views here.
global code


class WorkerView(generic.ListView):
    template_name = 'salary/worker_list.html'
    context_object_name = 'worker'

    def get_queryset(self):
        return Worker.objects.order_by('name__firstname')

class WorkerCreate(generic.CreateView):
    model = Worker
    success_url = reverse_lazy('salary:worker')
    fields = ['name', 'position', 'category']
    template_name = 'salary/worker_create.html'


class WorkCalcView(generic.ListView):
    template_name = 'salary/workcalc_list.html'
    context_object_name = 'workcalc'

    def get_queryset(self):
        return WorkCalc.objects.order_by('name')


class WorkCalcCreate(generic.CreateView):
    model = WorkCalc
    success_url = reverse_lazy('salary:workcalc')
    fields = ['name', 'time_range', 'cost']
    template_name = 'salary/workcalc_create.html'


class BonusWorkView(generic.ListView):
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

class BonusWorkEdit(generic.UpdateView):
    model = BonusWork
    template_name = 'salary/bonuswork_edit.html'
    success_url = reverse_lazy('salary:bonuswork')
    fields = ['date', 'model', 'worker', 'quantity', 'comment']


class AccountChangeView(generic.ListView):
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

class AccountChangeEdit(generic.UpdateView):
    model = AccountChange
    template_name = 'salary/accountchange_edit.html'
    success_url = reverse_lazy('salary:accountchange')
    fields = ['date', 'summ', 'worker', 'reason', 'comment']

class CategoryOfChangeView(generic.ListView):
    template_name = 'salary/categoryofchange_list.html'
    context_object_name = 'categoryofchange'

    def get_queryset(self):
        return CategoryOfChange.objects.order_by('name')


class CategoryOfChangeCreate(generic.CreateView):
    model = CategoryOfChange
    success_url = reverse_lazy('salary:categoryofchange')
    fields = ['name']
    template_name = 'salary/categoryofchange_create.html'


class TotalView(generic.ListView):
    template_name = 'salary/total_list.html'
    context_object_name = 'total'

    def get_queryset(self):
        total = Total.objects.filter(date__month=timezone.now().month)
        return total.all().order_by('worker__name')

def TotalCreate(request):
    workers = Worker.objects.all()
    total = Total.objects.filter(date__month=datetime.datetime.now().month)
    total_workers = [each.worker for each in total.all()]

    for each in workers:
        if each not in total_workers:
            Total.objects.create(worker=each)

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
    date = Total.objects.get(pk=total_id).date.month
    correction = AccountChange.objects.filter(
        worker=worker,
        date__month=date - 1,
        withholding=False,
        checking=True
    ).order_by('-date')
    bonus = BonusWork.objects.filter(
        worker=worker,
        date__month=date - 1,
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
    date = Total.objects.get(pk=total_id).date.month
    correction = AccountChange.objects.filter(
        worker=worker,
        date__month=date - 1,
        withholding=True,
        checking=True
    ).order_by('-date')
    bonus = BonusWork.objects.filter(
        worker=worker,
        date__month=date - 1,
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
    month = Total.objects.get(pk=total_id).date.month
    year = Total.objects.get(pk=total_id).date.year
    issued = Transaction.objects.filter(
        who_is=worker.name,
        category=worker.category,
        typeof=False,
        date__range=(
            datetime.datetime(year, month, 1),
            datetime.datetime(year, month + 1, 1)
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
    for total in total_list:
        total.balance_before_calc()
        total.accrual_calc()
        total.bonus_calc()
        total.withholding_calc()
        total.balance_after_calc()
        total.issued_calc()
        total.balance_now_calc()
    if code == '1':
        return HttpResponseRedirect(reverse('salary:worker'))
    elif code == '2':
        return HttpResponseRedirect(reverse('salary:total'))