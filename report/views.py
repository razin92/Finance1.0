from calc.models import Transaction
from salary.models import Total, BonusWork, Worker, AccountChange
from lib.models import Person, Pouch, Category, Staff
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render, reverse
from django.contrib.auth.decorators import login_required
from .models import ReportTransactionCategory, ReportTransactionPouch, ReportTransactionPerson
from .forms import WorkerFilter
from django.utils import timezone
from dateutil.parser import parse
import datetime


@login_required()
def report_transaction(request):
    person = Person.objects.order_by('firstname')
    staff_pouches = [x.name for x in Staff.objects.get(name__id=request.user.id).pouches.all()]
    pouch = Pouch.objects.filter(name__in=staff_pouches).order_by('name')
    template = loader.get_template('report/report_transaction.html')
    category = Category.objects.order_by('name')
    ReportTransactionPerson.objects.all().delete()
    ReportTransactionPouch.objects.all().delete()
    ReportTransactionCategory.objects.all().delete()
    context = {
        'person': person,
        'pouch': pouch,
        'category': category,
    }
    return HttpResponse(template.render(context, request))

@login_required()
def report_transaction_filter(request):
    from lib.models import Person, Category, Staff
    from calc.models import Transaction
    def get_filter(who_is, category, money, typeof, date_start, date_end):
        result = Transaction.objects.filter(
            who_is__firstname__in=who_is,
            category__name__in=category,
            money__name__in=money,
            typeof__in=typeof,
            date__range=[date_start, date_end],
            checking=True,
        ).order_by('-date', 'money', 'who_is')
        return result

    def create_report(result_set, start, end):

        def calculate(transaction, report):
            if transaction.typeof:
                report.income += transaction.sum_val
            else:
                report.outcome += transaction.sum_val
            report.save()

        for transaction in result_set:
            if transaction.money.type == 'SUM':
                report_by_who_is = ReportTransactionPerson.objects.get_or_create(
                        date_start=start,
                        date_end=end,
                        person=transaction.who_is
                    )

                calculate(transaction, report_by_who_is[0])

                report_by_category = ReportTransactionCategory.objects.get_or_create(
                        date_start=start,
                        date_end=end,
                        category=transaction.category
                    )
                calculate(transaction, report_by_category[0])
                report_by_money = ReportTransactionPouch.objects.get_or_create(
                        date_start=start,
                        date_end=end,
                        pouch=transaction.money
                    )

                calculate(transaction, report_by_money[0])

    template = 'report/report_transaction_filter.html'
    rqst = request.POST
    user = request.user
    # Генераторы списков (для значений по-умолчанию)
    firstname_set = Person.objects.values_list('firstname')
    money_set = Staff.objects.get(name__id=request.user.id).pouches.values_list('name')
    category_set = Category.objects.values_list('name').order_by('name')
    #Проверка вводных данных по дате, выставление значения по-умолчанию
    if 'date_start' in rqst and rqst['date_start']:
        date_start = rqst['date_start']
    else:
        date_start = datetime.datetime(timezone.now().year, timezone.now().month, 1).date()
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
    filter = get_filter(who_is, category, money, typeof, date_start, date_end)
    # НАДО ДОПИСАТЬ ПОДСЧЕТ ИТОГОВ!
    period = 'Период отчета c %s по %s' % (date_start, date_end)
    #Сводный отчет
    create_report(filter, date_start, date_end)
    by_category = ReportTransactionCategory.objects.filter(date_start=date_start, date_end=date_end).order_by('category__name')
    by_person = ReportTransactionPerson.objects.filter(date_start=date_start, date_end=date_end).order_by('person__firstname')
    by_pouch = ReportTransactionPouch.objects.filter(date_start=date_start, date_end=date_end).order_by('pouch__name')

    context = {
        'transaction': filter,
        'user': user,
        'period': period,
        'by_category': by_category,
        'by_person': by_person,
        'by_pouch': by_pouch,
        'date_start': date_start,
        'date_end': date_end,
    }

    return render(request, template, context)

def report_transaction_detail(request):
    pass

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
        'result2': result2,
    }

    return render_to_response(template, context)