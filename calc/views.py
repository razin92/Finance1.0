from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.http import HttpResponse, request, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from lib.models import Pouch, Staff, Category, Person
from report.models import TransactionChangeHistory
from django.utils import timezone
from .forms import TransactionForm, TransactionEditForm
from .models import Transaction
import datetime

#Список транзакцй
@login_required()
def TransactionView(request):
    template = 'calc/transaction.html'
    user = request.user
    user_id = user.pk
    date_start = datetime.datetime(timezone.now().year, timezone.now().month, 1).date()
    date_end = datetime.datetime(timezone.now().year, timezone.now().month, timezone.now().day, hour=23, minute=59)
    get_permission = Staff.objects.get(
        name__id=user_id
    )
    permitted_pouches = [x for x in get_permission.pouches.all()] #Разрешенные кошельки (lib.staff.pouches)
    if user.is_superuser:
        transaction = Transaction.objects.filter(
            money__in = permitted_pouches,
            date__range=[date_start, date_end],
        ).order_by('-date')
    else:
        transaction = Transaction.objects.filter(
            money__in = permitted_pouches,
            checking = True,
            date__range = [date_start, date_end]
        ).order_by('-date')
    pouch = Pouch.objects.filter(
        name__in = permitted_pouches
    ).order_by('name')
    context = {
        'transaction': transaction,
        'pouch': pouch,
        'user': user
    }
    return render_to_response(template, context)

#Детально о транзакции
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
    template = 'calc/transaction_create.html'
    form = TransactionForm(request.POST, user_id=request.user.pk)
    error = '* Обязательны к заполнению'
    context = {
        'form': form,
        'kind': kind,
        'error': error
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
        return HttpResponseRedirect(reverse('calc:transaction_edit', args={transaction_id, }))
    return HttpResponseRedirect(reverse('calc:transaction'))

def CreateTransactionChangeHistory(data):
    data_get=data.get
    #Создается объект истории с текущими данными транзакции
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
    #Обновленные данные транзакции в объект истории
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
    data = get_data()[1]
    #активация отмененной транзакции
    if transaction.checking:
        return HttpResponseRedirect(reverse('calc:changer', kwargs={'transaction_id': transaction_id, 'number': 1, }))
    form = TransactionEditForm(request.POST or None, instance=transaction, user_id=request.user.pk)
    CreateTransactionChangeHistory(data)
    if form.is_valid():
        form.save()
        data = get_data()[1]
        UpdateTransactionChangeHistory(data)
        return HttpResponseRedirect(reverse('calc:changer', kwargs={'transaction_id': transaction_id, 'number': 0, }))
    message = "Внимание! Выход без сохранения удалит транзакцию"
    context = {
        'form': form,
        'message': message
    }
    return render(request, template, context)

@login_required()
def delete_accept(request, transaction_id):
    user = request.user
    template = 'calc/delete_confirm.html'
    transaction = Transaction.objects.get(id=transaction_id)
    message = 'Вы действительно хотите удалить транзакцию' \
              'ID = %s' \
              'Сумма = %s' \
              'Категория = %s' \
              % (transaction.id, transaction.sum_val, transaction.category)
    context = {

    }
    pass

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

