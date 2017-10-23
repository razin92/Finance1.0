from django.shortcuts import render, get_object_or_404, render_to_response, redirect
from django.http import HttpResponse, request, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from lib.models import Pouch, Staff, Category, Person
from django.utils import timezone
from .forms import TransactionForm
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
def changer(request, transaction_id):
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
    return HttpResponseRedirect(reverse('calc:transaction'))

@login_required()
class TransactionEdit(generic.UpdateView):
    model = Transaction
    pass

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

