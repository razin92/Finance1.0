from calc.models import Transaction
from salary.models import Total, BonusWork, Worker, AccountChange
from lib.models import Person, Pouch, Category, Staff
from django.template import loader
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from .models import ReportTransactionCategory, ReportTransactionPouch, ReportTransactionPerson
from .forms import WorkerFilter
from django.utils import timezone
import datetime

@login_required()
def report_transaction(request):
    person = Person.objects.order_by('firstname')
    staff_pouches = [x.name for x in Staff.objects.get(name__id=request.user.id).pouches.all()]
    pouch = Pouch.objects.filter(name__in=staff_pouches)
    template = loader.get_template('report/report_transaction.html')
    category = Category.objects.order_by('name')
    context = {
        'person': person,
        'pouch': pouch,
        'category': category,
    }
    return HttpResponse(template.render(context, request))

@login_required()
def report_transaction_filter(request):
    template = 'report/report_transaction_filter.html'
    rqst = request.POST
    user = request.user
    # Генераторы списков (для значений по-умолчанию)
    firstname_set = [x.firstname for x in Person.objects.all()]
    money_set = [x.name for x in Staff.objects.get(name__id=request.user.id).pouches.all()]
    category_set = [x.name for x in Category.objects.all()]
    #Проверка вводных данных по дате, выставление значения по-умолчанию
    if 'date_start' in rqst and rqst['date_start']:
        date_start = rqst['date_start']
    else:
        date_start = datetime.datetime(timezone.now().year, timezone.now().month, 1)
    if 'date_end' in rqst and rqst['date_end']:
        date_end = rqst['date_end']
    else:
        date_end = datetime.datetime(timezone.now().year, timezone.now().month, timezone.now().day, hour=23, minute=59)
    #Обработка данных из POST запроса
    who_is = rqst.getlist('who_is', firstname_set)
    category = rqst.getlist('category', category_set)
    money = rqst.getlist('money', money_set)
    typeof = rqst.getlist('typeof', ['True', 'False'])
    #Фильтр транзакций
    filter = Transaction.objects.filter(
        who_is__firstname__in=who_is,
        category__name__in=category,
        money__name__in=money,
        typeof__in=typeof,
        date__range=[date_start, date_end]
    ).order_by('-date', 'money', 'who_is')
    # НАДО ДОПИСАТЬ ПОДСЧЕТ ИТОГОВ!
    error = 'Не верные данные'
    period = 'Период отчета c %s по %s' % (date_start.strftime('%d-%m-%Y'), date_end.strftime('%d-%m-%Y'))

    context = {
        'transaction': filter,
        'error': error,
        'user': user,
        'period': period
    }
    return render_to_response(template, context)

@login_required()
def report_salary_total(request):
    pass

@login_required()
def report_salary_bonus(request):
    pass

@login_required()
def report_workers(request):
    form = WorkerFilter
    user = request.user
    template = loader.get_template('report/report_workers.html')
    context = {
        'form': form,
        'user': user,
    }
    return HttpResponse(template.render(context, request))

@login_required()
def report_workers_filter(request):
    user = request.user
    rqst = request.POST
    template = 'report/report_workers_filter.html'
    workers_id = rqst.getlist('worker')
    job_list1 = BonusWork.objects.filter(worker__id__in=workers_id, date__range=(rqst['date_start'], rqst['date_end']))
    job_list2 = AccountChange.objects.filter(worker__id__in=workers_id, date__range=(rqst['date_start'], rqst['date_end']))
    workers = Worker.objects.filter(id__in=workers_id).order_by('name')
    result = {job_list1.filter(worker=x).order_by('-date', 'worker') for x in workers.all()}
    result2 = {job_list2.filter(worker=x).order_by('-date', 'worker') for x in workers.all()}
    context = {
        'user': user,
        'workers': workers,
        'result': result,
    }

    return render_to_response(template, context)