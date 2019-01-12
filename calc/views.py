from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.http import HttpResponse, request, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from lib.models import Pouch, Staff, Category, Person
from report.models import TransactionChangeHistory, BalanceStamp
from django.utils import timezone
from salary.models import WorkReport
from django.views import View
from .forms import TransactionForm, TransactionEditForm, MonthForm, WorkReportTransactionForm
from .models import Transaction
import datetime


@login_required()
def TransactionView(request):
    """
    Displays list of all transaction within one month filtered by
    staff.pouches and user permissions
    """
    template = 'calc/transaction.html'
    form = MonthForm
    user = request.user
    rqst = request.POST

    if 'select_month' in rqst and rqst['select_month']:
        month = rqst['select_month']
        year = rqst['select_year']
    else:
        month = str(timezone.now().month)
        year = datetime.datetime.now().year
    staff = get_object_or_404(Staff,
        name__id=user.pk)
    permitted_pouches = [x for x in staff.pouches.all()]
    transaction = Transaction.objects.filter(
        money__in=permitted_pouches,
        date__month=month,
        date__year=year
    ).order_by('-date')
    if not user.is_superuser:
        transaction = transaction.filter(checking=True)
    pouch = staff.pouches.order_by('name')

    month_name = MonthForm.month[int(month)][1]
    context = {
        'transaction': transaction,
        'pouch': pouch,
        'user': user,
        'form': form,
        'month_name': month_name,
        'year': year
    }
    return render(request, template, context)


@login_required()
def TransactionDetailView(request, pk):
    template = 'calc/transaction_detail.html'
    user_id = request.user.pk
    user = User.objects.get(pk=user_id)
    transaction = Transaction.objects.get(pk=pk)
    context = {
        'transaction': transaction,
        'user': user
    }
    return render(request, template, context)


@login_required()
def TransactionCreate(request, kind):
    """
    :param kind: points the type of transaction: income(1) or spending(0)
    Creates transaction
    """
    template = 'calc/transaction_create.html'
    form = TransactionForm(request.POST or None, user_id=request.user.pk)
    context = {
        'form': form,
        'kind': kind,
    }
    return render(request, template, context)


#Проводка/отмена транзакции
@login_required()
def changer(request, transaction_id, number):
    transaction = get_object_or_404(Transaction, pk=transaction_id)
    pouch = get_object_or_404(Pouch, pk=transaction.money.id)
    #проверка на проведение транзакции, запись баланса в текущий кошелек
    if transaction.checking:
        if transaction.typeof:
            transaction.checking = False
            pouch.balance -= transaction.sum_val
        else:
            transaction.checking = False
            pouch.balance += transaction.sum_val
    else:
        if transaction.typeof:
            transaction.checking = True
            pouch.balance += transaction.sum_val
        else:
            transaction.checking = True
            pouch.balance -= transaction.sum_val

    transaction.save()
    pouch.save()
    if number == '1':
        if not transaction.checking:
            def get_data():
                transaction = get_object_or_404(Transaction, pk=transaction_id)
                data = {
                    'id': transaction.id,
                    'date': transaction.date,
                    'sum_val': transaction.sum_val,
                    'category': transaction.category.name,
                    'who_is': '%s %s' % (transaction.who_is.firstname, transaction.who_is.secondname),
                    'comment': transaction.comment,
                    'money': '%s %s' % (transaction.money.name, transaction.money.comment),
                    'typeof': transaction.typeof,
                    'date_2': transaction.create_date,
                    'creator': transaction.creator.username,
                    'changer': request.user.username
                }
                return data
            data = get_data()
            CreateTransactionChangeHistory(data)
        return HttpResponseRedirect(reverse('calc:transaction_edit', args={transaction_id, }))
    return HttpResponseRedirect(reverse('calc:transaction'))


# Метки изменения баланса
def CreateBalanceStamp(transaction, history, reason):
    balance_before = transaction.money.balance
    if transaction.checking:
        if transaction.typeof:
            balance_after = balance_before + transaction.sum_val
        else:
            balance_after = balance_before - transaction.sum_val
    else:
        if transaction.typeof:
            balance_after = balance_before - transaction.sum_val
        else:
            balance_after = balance_before + transaction.sum_val

    stamp = BalanceStamp.objects.create(
        pouch=transaction.money,
        sum_val=transaction.sum_val,
        balance_before=balance_before,
        balance_after=balance_after,
        transaction=transaction,
        reason=reason,
    )
    stamp.transaction_change = history
    stamp.save()
    return stamp


def CreateTransactionChangeHistory(data):
    data_get=data.get
    # Создается объект истории с текущими данными транзакции
    TransactionChangeHistory.objects.create(
        transaction_id=data_get('id'),
        date_before=data_get('date'),
        sum_val_before='%s' % data_get('sum_val'),
        category_before='%s' % data_get('category'),
        who_is_before='%s' % data_get('who_is'),
        comment_before='%s' % data_get('comment'),
        money_before='%s' % data_get('money'),
        typeof_before=data_get('typeof'),
        typeof_after=data_get('typeof'),
        date_of_create=data_get('date_2'),
        date_of_change=timezone.now(),
        creator='%s' % data_get('creator'),
        changer='%s' % data_get('changer'),
    )

def UpdateTransactionChangeHistory(data):
    # Обновленные данные транзакции в объект истории
    data_get = data.get
    history = TransactionChangeHistory.objects.last()
    history.date_after = data_get('date')
    history.sum_val_after = '%s' % data_get('sum_val')
    history.category_after = '%s' % data_get('category')
    history.who_is_after = '%s' % data_get('who_is')
    history.comment_after = '%s' % data_get('comment')
    history.money_after = '%s' % data_get('money')
    history.date_of_change = timezone.now()
    history.save()
    return history


@login_required()
def TransactionEdit(request, transaction_id):
    template = 'calc/transaction_edit.html'
    def get_data():
        transaction = get_object_or_404(Transaction, pk=transaction_id)
        data = {
            'id': transaction.id,
            'date': transaction.date,
            'sum_val': transaction.sum_val,
            'category': transaction.category.name,
            'who_is': '%s %s' % (transaction.who_is.firstname, transaction.who_is.secondname),
            'comment': transaction.comment,
            'money': '%s %s' % (transaction.money.name, transaction.money.comment),
            'typeof': transaction.typeof,
            'date_2': transaction.create_date,
            'creator': transaction.creator.username,
            'changer': request.user.username
        }
        return transaction, data
    transaction = get_data()[0]
    #активация отмененной транзакции
    if transaction.checking:
        return HttpResponseRedirect(reverse('calc:changer', kwargs={'transaction_id': transaction_id, 'number': 1, }))
    form = TransactionEditForm(request.POST or None, instance=transaction, user_id=request.user.pk)
    if form.is_valid():
        form.save()
        data = get_data()[1]
        transaction = get_data()[0]
        history = UpdateTransactionChangeHistory(data)
        transaction.checking = True
        CreateBalanceStamp(transaction, history, 'Изменение')
        return HttpResponseRedirect(reverse('calc:changer', kwargs={'transaction_id': transaction_id, 'number': 0, }))
    else:
        CreateBalanceStamp(transaction, None, '+/-')
    message = "Внимание! Выход без сохранения удалит транзакцию"
    context = {
        'form': form,
        'message': message
    }
    return render(request, template, context)


@login_required()
def calculate(request, kind):
    form = TransactionForm(request.POST, user_id=request.user.pk)

    #Проверка на тип транзакции (приход = 1/расход = 0)
    def check(kind):
        return kind == '1'

    #Если форма валидна, заносим транзакцию в базу
    if request.method == 'POST' and form.is_valid():
        transaction = Transaction.objects.create(**form.cleaned_data)
        transaction.creator = request.user
        pouch = get_object_or_404(Pouch, pk=transaction.money.id)
        sum = transaction.sum_val
        #Калькуляция в зависимости от типа транзакции
        if check(kind):
            transaction.typeof = True
            pouch.balance += sum
        else:
            pouch.balance -= sum
        transaction.save()
        pouch.save()
        CreateBalanceStamp(transaction, None, 'Создание')
        return HttpResponseRedirect(reverse('calc:transaction'))
    else:
        template = 'calc/transaction_create.html'
        error = 'Проверьте правильность вводимых данных!'
        context = {
            'form': form,
            'error': error,
            'kind': kind,
        }
        return render(request, template, context)


class ReportsMoney(View):

    template = 'calc/reports_money.html'

    def get(self, request):
        user = request.user
        reports_list = WorkReport.objects.filter(income__gt=0, deleted=False, working_date__gt='2018-09-30')
        total_sum = reports_list.values('income').aggregate(Sum('income'))['income__sum']
        got = reports_list.filter(transaction__isnull=False)\
            .values_list('income')\
            .aggregate(Sum('income'))['income__sum']
        not_got = reports_list.filter(transaction__isnull=True)\
            .values_list('income')\
            .aggregate(Sum('income'))['income__sum']
        exclude_list = ['filling_date', 'stored',
                        'tagged_coworker', 'transaction',
                        'coworkers_qt_ty', 'confirmed', 'deleted',
                        'cost', 'comment', 'admin_comment', 'hours_qty'
                        ]
        headers = [x for x in WorkReport._meta.get_fields() if x.name not in exclude_list]
        context = {
            'reports_list': reports_list if user.is_superuser else None,
            'headers': headers,
            'total_sum': total_sum if user.is_superuser else None,
            'got': got or 0,
            'not_got': not_got or 0
        }
        return render(request, self.template, context)


def set_default_color(color):
    category = Category.objects.all()
    for each in category:
        each.color = '3E3E3E'
        each.save()
    return print('done')


class WorkReportTransaction(View):
    template = 'calc/report_confirmation.html'

    def get(self, request):
        report = get_object_or_404(WorkReport, id=request.GET.get('report_id', 0))
        form = WorkReportTransactionForm(None, user_id=request.user.id, report=report)
        context = {
            'form': form,
            'report': report
        }
        return render(request, self.template, context)

    def post(self, request):
        report = get_object_or_404(WorkReport, id=request.GET.get('report_id', 0))
        form = WorkReportTransactionForm(data=request.POST, user_id=request.user.pk, report=report)
        # Если форма валидна, заносим транзакцию в базу
        if form.is_valid():
            transaction = Transaction.objects.create(**form.cleaned_data)
            transaction.creator = request.user
            pouch = get_object_or_404(Pouch, pk=transaction.money.id)
            sum = transaction.sum_val
            # Калькуляция
            transaction.typeof = True
            pouch.balance += sum
            transaction.save()
            pouch.save()
            report.transaction = transaction
            report.save()
            CreateBalanceStamp(transaction, None, 'Создание')
            return HttpResponseRedirect(reverse('calc:reports_money'))
        else:
            context = {
                'form': form,
                'report': report
            }
            return render(request, self.template, context)