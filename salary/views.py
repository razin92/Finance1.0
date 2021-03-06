from django.views.generic import View, ListView, CreateView, UpdateView
from .models import Worker, WorkCalc, BonusWork, AccountChange, \
    CategoryOfChange, Total, WorkReport, Work
from calc.models import Transaction
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Sum
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from .forms import BonusWorkForm, AccountChangeForm, \
    WorkReportUserForm, WorkForm, WorkFilterForm, MyWorkFilterForm, \
    ReportConfirmationForm, WorkReportForm, WorkReportTaggedForm, \
    MassBonusForm
from ast import literal_eval
from calc.forms import MonthForm
from .auth import AuthData
import logging
import datetime
import calendar
import re
# Create your views here.
global code

logging = logging.getLogger(__name__)

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

class MassBonus(View):

    def __init__(self):
        super(MassBonus, self).__init__()
        self.template = 'salary/bonuswork_create.html'
        self.form = MassBonusForm

    def get(self, request):
        form = self.form(None)
        return render(request, self.template, context={'form': form})

    def post(self, request):
        form = self.form(request.POST or None)
        if form.is_valid():
            for each in request.POST.getlist('workers'):
                BonusWork.objects.create(
                    model=WorkCalc.objects.get(id=int(request.POST['model'])),
                    worker=Worker.objects.get(id=int(each)),
                    quantity=request.POST['quantity'],
                    date=request.POST['date'],
                    comment=request.POST['comment'],
                )
            return HttpResponseRedirect(reverse('salary:bonuswork'))
        return render(request, self.template, context={'form': form})

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
    today = datetime.date.today()
    if 'select_month' in rqst and rqst['select_month']:
        date = rqst['select_month']
    else:
        date = today.month
    def get_queryset(date):
        total = Total.objects.filter(
            date__month=date,
            date__year=today.year
        ).order_by('worker__name')
        return total
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
    workers = Worker.objects.filter(fired=False)
    today = datetime.date.today()
    total = Total.objects.filter(date__month=today.month, date__year=today.year)
    total_workers = [each.worker for each in total.all()]
    month_now = datetime.date.today().replace(day=1)

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
            datetime.date(year, month, 1),
            datetime.date(next_year, next_month, 1)
        ),
        checking=True
    ).order_by('-date')
    return render(request, 'salary/total_issued_detail.html', {
        'worker': worker,
        'issued': issued
    })


@login_required()
def calculate(request, code):
    today = datetime.date.today()
    month = request.GET.get('month', today.month)
    total_list = Total.objects.filter(date__month=month, date__year=today.year)
    date_now = {'month': month, 'year': today.year}
    for total in total_list:
        total.calculate(date=date_now)
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
    """
    View for creating the report
    if a user was tagged in the ones work,
    the first action: confirm or cancel work
    """
    #
    template = 'salary/work_report.html'
    message = ''

    def get(self, request):
        user = request.user.id
        form = None
        tagged_work = None
        if self.can_make_report(request.user):
            tagged_work = self.tagged_work(user) # Проверка на участие в других работах
            form = WorkReportUserForm(None, user_id=user)
            if tagged_work:
                form = self.make_form(tagged_work, user) # Формирование новой формы со скрытыми полями
                self.message = '%s отметил вас в работе' % Worker.objects.get(user=tagged_work.user)
        else:
            self.message = 'Недостаточно прав'
        context = {
            'form': form,
            'tagged_work': tagged_work,
            'message': self.message
        }
        return render(request, self.template, context)

    def post(self, request):
        user = request.user.id
        form = WorkReportUserForm(request.POST, user_id=user)
        context = {
            'form': form,
            'message': self.message,
        }
        if form.is_valid() or 'new' in request.POST:
            new_object = self.WorkReportCreate(request.POST, request.user)
            if new_object is not None:
                coworkers = request.POST.getlist('coworker', '')
                for x in coworkers:
                    new_object.coworker.add(x)
                if 'new' in request.POST:
                    # добавить счетчик отмеченных, если была принята совместная работа
                    WorkReport.objects.get(id=request.POST['tagged_id']).untag_coworker()
                    new_object.coworkers_qt_ty = 0
                    new_object.save()
                if coworkers != '' and new_object.coworkers_qt_ty == 1:
                    new_object.tag_coworker()

                context['message'] = 'Успех'
            else:
                context['message'] = 'Объект уже существует'
        if 'new' in request.POST:
            return HttpResponseRedirect(reverse('salary:work_report_create'))
        return render(request, self.template, context)

    def WorkReportCreate(self, data, user):
        try:
            result = WorkReport.objects.get_or_create(
                working_date=data['working_date'],
                hours_qty=data['hours_qty'],
                user=user,
                work=Work.objects.get(pk=data['work']),
                quarter=data['quarter'],
                building='%s%s' % (data['building'], data['building_litera']),
                apartment=self.apartment(data),
                income=self.get_income(data['income']),
                comment=data['comment']
            )
            if result[1]:
                logging.debug('*success* %s' % data)
                return result[0]
            # если отчет уже имеется, но выходит в отмеченных, добавить к счетчику отмеченных
            WorkReport.objects.get(id=data['tagged_id']).untag_coworker()
            return None
        except IntegrityError:
            logging.debug('*error* %s' % data)
            return None


    def get_parameter(self, data, name):
        if name in data:
            try:
                return data[name]
            except:
                return ''
        return ''

    def apartment(self, request):
        if request['apartment'] == '':
            return None
        else:
            return request['apartment']

    def get_income(self, data):
        if data == '':
            return None
        return data

    def tagged_work(self, user_id, last_work=None):
        worker = Worker.objects.get(user_id=user_id)
        work = WorkReport.objects.filter(tagged_coworker=True, coworker__id=worker.id)
        for each in work:
            if each.check_report(user_id):
                last_work = each
                break
        return last_work

    def make_form(self, work_object, user_id):
        return WorkReportTaggedForm(None, work=work_object, user_id=user_id)

    def can_make_report(self, user):
        get_worker = Worker.objects.filter(user=user)
        if get_worker.__len__() > 0:
            return True
        return False


def WorkerReportUserEdit(request):
    template = 'salary/work_report.html'
    work_id = request.GET['wid']
    work = get_object_or_404(
        WorkReport,
        id=work_id,
        user=request.user,
        confirmed=False
    )
    form = WorkReportForm(request.POST or None, instance=work)
    if form.is_valid():
        form.save()
        work.working_date = request.POST['working_date']
        if work.coworker.all().__len__() != 0 and work.coworkers_qt_ty == 1:
            work.tag_coworker()
        work.save()
        rqst = request.POST
        logging.info('%s edited by %s (%s %s %s(%s) %s)->(%s)' %
                     (work.id, request.user,
                      work.working_date,
                      '-'.join(['%s' % work.quarter,'%s' % work.building, '%s' % work.apartment]),
                      work.work.name, work.work.id, ['%s(%s)' % (x.name, x.id) for x in work.coworker.all()],
                      rqst))
        return HttpResponseRedirect(reverse('salary:my_reports_list', kwargs={'page': 1}))
    context = {
        'form': form,
    }
    return render(request, template, context)


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
    """
    View for workers
    """
    template = 'salary/work_list.html'
    today = datetime.date.today()
    last_day = calendar.monthcalendar(today.year, today.month)[1]

    def get(self, request, page=1):
        form = MyWorkFilterForm(request.POST or None)
        data = WorkReport.objects.filter(
            user=request.user,
            working_date__month=self.today.month,
            working_date__year=self.today.year
        ).order_by('deleted', 'confirmed', '-working_date')
        cost_sum = data.filter(confirmed=True,
                               deleted=False,
                               stored=False).values('cost').aggregate(Sum('cost'))['cost__sum']
        income_sum = data.filter(deleted=False).values('income').aggregate(Sum('income'))['income__sum']
        gave = data.filter(deleted=False, transaction__isnull=False)\
            .values('income').aggregate(Sum('income'))['income__sum']
        not_gave = data.filter(deleted=False, transaction__isnull=True)\
            .values('income').aggregate(Sum('income'))['income__sum']
        exclude_list = ['filling_date', 'user', 'stored', 'tagged_coworker', 'transaction', 'coworkers_qt_ty']
        header = [x for x in WorkReport._meta.get_fields() if x.name not in exclude_list]
        splitter = Paginator(data, 25)
        split_data = splitter.page(page)
        context = {
            'header': header,
            'data': split_data.object_list,
            'pages': split_data,
            'form': form,
            'cost_sum': cost_sum or 0,
            'income': income_sum or 0,
            'gave': gave or 0,
            'not_gave': not_gave or 0
        }
        return render(request, self.template, context)

    def post(self, request, page):
        form = MyWorkFilterForm(request.POST or None)
        start = request.POST['date_start']
        end = request.POST['date_end']
        data = WorkReport.objects.filter(
            user=request.user,
            working_date__range=(start, end)
        ).order_by('confirmed', '-working_date')
        cost_sum = data.values('cost').aggregate(Sum('cost'))
        exclude_list = ['filling_date', 'user']
        header = [x for x in WorkReport._meta.get_fields() if x.name not in exclude_list]
        context = {
            'header': header,
            'data': data,
            'form': form,
            'cost_sum': cost_sum['cost__sum'],
        }
        return render(request, self.template, context)

class ReportsList(View):
    """
    View for Head person
    """
    template = 'salary/work_reports_list.html'

    def get(self, request):
        page = request.GET.get('page', 1)  # Getting page number
        per_page = request.GET.get('per_page', 25)
        #dupes = self.get_duplicate(WorkReport)  # Dupes checking
        if 'confirmed' in request.GET or 'deleted' in request.GET or 'stored' in request.GET:
            data = self.additional_filters(request)
        else:
            data = WorkReport.objects.all().order_by(
                'deleted', 'confirmed', 'stored', '-confirmed',
                '-working_date', 'quarter', 'building', 'apartment')
        data_per_page = Paginator(data, per_page)
        result = data_per_page.page(page)
        exclude_list = ['filling_date', 'stored', 'tagged_coworker', 'transaction', 'coworkers_qt_ty']
        salary = self.salary_of_workers()
        header = [x for x in WorkReport._meta.get_fields() if x.name not in exclude_list]  # Headers for table
        not_confirmed, stored = self.counter()
        context = {
            'header': header,
            'data': result.object_list,
            'pages': result,
            'salary': salary,
            'filter': self.get_filter(request),
            'not_confirmed': not_confirmed,
            'stored': stored,
        }
        return render(request, self.template, context)

    def get_duplicate(self, data):
        nowadays_month = datetime.datetime.today().month
        duplicates = data.objects.filter(
            working_date__month=nowadays_month, deleted=False, apartment__isnull=False).\
            values('id', 'working_date', 'work__name', 'quarter', 'building', 'apartment')
        '''
        dupl = WorkReport.objects.filter(
            quarter__in=[x['quarter'] for x in duplicates],
            building__in=[x['building'] for x in duplicates],
            apartment__in=[x['apartment'] for x in duplicates],
        ).order_by('quarter', 'building', 'apartment', '-working_date')
        '''
        return duplicates

    def counter(self):
        work_list = WorkReport.objects.all()
        not_confirmed = work_list.filter(confirmed=False, deleted=False, stored=False).__len__()
        stored = work_list.filter(confirmed=False, deleted=False, stored=True).__len__()
        return not_confirmed, stored,

    def salary_aggregator(self, user):
        reports_now_a_month = WorkReport.objects.filter(
            working_date__month=datetime.datetime.now().month,
            working_date__year=datetime.datetime.now().year
        )
        result = reports_now_a_month.filter(
            user=user).aggregate(Sum('cost'))['cost__sum']
        return result or 0

    def salary_of_workers(self):
        workers = Worker.objects.filter(can_make_report=True)
        result = ['%s: %s' %
                  (each.name,'{:,}'.format(self.salary_aggregator(each.user))) for each in workers]
        return ' / '.join(result)

    def additional_filters(self, request):
        confirmed = request.GET.get('confirmed', False)
        stored = request.GET.get('stored', False)
        deleted = request.GET.get('deleted', False)
        data = WorkReport.objects.filter(
            confirmed=confirmed,
            stored=stored,
            deleted=deleted
        ).order_by('deleted', 'confirmed', '-working_date',
                'quarter', 'building', 'apartment')
        return data

    def get_filter(self, request):
        data = re.split(r'[?&]page=[0-9]+', request.META['QUERY_STRING'])
        return data[0]


class ReportHistory(View):
    """
    Displays the list of all reports on selected address
    """
    def get(self, request):
        template = 'salary/work_report_history.html'
        work = None
        work_list = None
        address = None
        cost = None
        if 'id' in request.GET:
            work = get_object_or_404(WorkReport, id=request.GET['id'])
        if work:
            work_list = WorkReport.objects.filter(
                quarter=work.quarter,
                building=work.building,
                apartment=work.apartment,
                deleted=False
            ).order_by('-working_date')
            address = '-'.join(
                [str(work.quarter), str(work.building), str(work.apartment) if work.apartment else '#'])
            cost = work_list.filter(confirmed=True).values('cost').aggregate(Sum('cost'))['cost__sum']
        context = {
            'info': work_list,
            'address': address,
            'cost': cost
        }
        return render(request, template, context)

class ReportConfirmation(View):
    """
    View for Head person
    """
    template = 'salary/report_confirmation.html'

    def get(self, request):
        rqst = request.GET
        form = ReportConfirmationForm(None)
        data, result, info, cost = '', '', None, None

        if request.user.has_perm('salary.change_workreport'):
            data = WorkReport.objects.filter(
                confirmed=False, deleted=False, stored=False).order_by(
                '-working_date', 'user').distinct()
            if 'action' in  rqst and rqst['action'] == 'Подтвердить':
                result = self.update_report(
                    rqst['id'], rqst, rqst.get('cost', None), confirmed=True)
            elif 'action' in  rqst and rqst['action'] == 'Удалить':
                result = self.update_report(rqst['id'], rqst, deleted=True)
            elif 'action' in  rqst and rqst['action'] == 'Отложить':
                result = self.update_report(rqst['id'], rqst, stored=True)
            elif 'id' in rqst:
                data = WorkReport.objects.filter(
                    id=rqst['id'], deleted=False, confirmed=False)
                if data.__len__() > 0:
                    form = ReportConfirmationForm(instance=data[0])

        if data.__len__() > 0:
            data = data[0]
            info = self.work_on_this_address(data)
            cost = info.filter(confirmed=True).values('cost').aggregate(Sum('cost'))['cost__sum']

        context = {
            'data': data,
            'form': form,
            'result': result,
            'info': info,
            'cost': cost
        }
        return render(request, self.template, context)

    def update_report(self, id, comment, cost=None, deleted=False,
                      confirmed=False, stored=False):
        admin_comment = ''
        if 'admin_comment' in comment:
            admin_comment = comment['admin_comment']
        data = WorkReport.objects.get(id=id)
        if cost == '':
            cost = None
        data.cost = cost
        data.confirmed = confirmed
        data.deleted = deleted
        data.admin_comment = admin_comment
        data.stored = stored
        data.save()
        message = 'Отчет №%s, выполненный %s подтвержден' % (id, data.user)
        if confirmed:
            logging.info('Report %s *confirmed* with cost %s by %s' % (
                id, cost, self.request.user))
        elif deleted:
            message = 'Отчет №%s, выполненный %s удален' % (id, data.user)
            logging.info('Report %s *deleted* with cost %s by %s' % (
                id, cost, self.request.user))
        elif stored:
            message = 'Отчет №%s, выполненный %s отложен' % (id, data.user)
            logging.info('Report %s *stored* with cost %s by %s' % (
                id, cost, self.request.user))
        return message

    def work_on_this_address(self, data):
        result = WorkReport.objects.filter(
            quarter=data.quarter,
            building=data.building,
            apartment=data.apartment,
            deleted=False,
        ).exclude(id=data.id).order_by('-working_date')
        return result


class ConsolidatedReport(View):
    """
    Displays detailed reports for head person
    """
    data = {}

    def get(self, request):
        self.data = self.parameters(request)
        template = 'salary/work_reports_detailed.html'
        form = WorkFilterForm(None)
        #all_work = None
        report = self.work_filter(self.data)
        date = '%s - %s' % (self.data['date_start'], self.data['date_end'])
        if self.data['do_not_use_date']:
            date = 'За весь период'
        all_work = report.values(
            'quarter', 'building', 'apartment', 'work', 'working_date').distinct()
        context = {
            'form': form,
            'report': self.worker_sorter(report),
            'header': self.header(),
            'work_counter': self.work_counter_single(report),
            'dates': date,
            'group_work': self.work_counter_group(report),
            'all_work': all_work
        }
        logging.debug(context)
        return render(request, template, context)

    def work_filter(self, parameters):
        result = WorkReport.objects.filter(
            work__id__in=parameters['work_list'],
            user__worker__id__in=parameters['workers'],
            confirmed=True,
            deleted=False
        ).order_by('-working_date', 'work__name')
        if not parameters['do_not_use_date']:
            result = result.filter(
                working_date__range=(
                    parameters['date_start'],
                    parameters['date_end']
                )
            )
        if parameters['quarter']:
            result = result.filter(quarter__in=parameters['quarter'])
        if parameters['building']:
            result = result.filter(building__in=parameters['building'])
        if parameters['apartment']:
            result = result.filter(apartment__in=parameters['apartment'])
        logging.debug('Work: %s %s' % (result.__len__(), [x.id for x in result]))
        return result

    def parameters(self, request):
        do_not_use_date = request.GET.get('do_not_use_date', False)
        work_list = request.GET.getlist('work', [x[0] for x in Work.objects.values_list('id')])
        date_start = datetime.date.today().replace(day=1)
        date_end = datetime.date.today()
        quarter = self.get_list(request, 'quarter')
        building = self.get_list(request, 'building')
        apartment = self.get_list(request, 'apartment')
        if 'working_date_start' in request.GET:
            date_start = request.GET['working_date_start']
        if 'working_date_end' in request.GET:
            date_end = request.GET['working_date_end']
        workers = request.GET.getlist(
            'workers', [x[0] for x in Worker.objects.values_list('id').filter(can_make_report=True)])
        data = {
            'work_list': work_list,
            'date_start': date_start,
            'date_end': date_end,
            'workers': workers,
            'quarter': quarter,
            'building': building,
            'apartment': apartment,
            'do_not_use_date': do_not_use_date
        }
        logging.debug(data)
        return data

    def worker_sorter(self, report):
        result = [report.filter(
            user__worker__id=int(each),
        ) for each in self.data['workers']]
        return result

    def header(self):
        exclude_list = ['filling_date', 'deleted', 'confirmed', 'stored',
                        'tagged_coworker', 'transaction', 'coworkers_qt_ty']
        header = [x for x in WorkReport._meta.get_fields() if x.name not in exclude_list]
        return header

    def work_counter_single(self, report):
        work_counter = ['%s: %s' %
                (Work.objects.get(id=int(x)),
                 report.filter(
                     work__id=int(x),
                     coworker__isnull=True).__len__()
                 ) for x in self.data['work_list'] if
                        report.filter(work__id=int(x), coworker__isnull=True).__len__() > 0
                 ]
        return work_counter

    def work_counter_group(self, report):
        work_list_group = report.filter(coworker__isnull=False).\
            order_by('quarter', 'building', 'apartment', 'work').distinct()
        return work_list_group

    def get_list(self, request, data, default=None):
        if request.GET.get(data, '') != '':
            return request.GET[data].split(',')
        return default


# Subscriber searcher
class SubsSearcher(AuthData):

    def get(self, request):
        template = 'salary/subs_search.html'
        address = request.GET.get('address', None)
        search_data, result, balance = None, None, None
        if address:
            search_data = self.data_splitter(address)
            data = self.data_extractor(search_data)
            result = []
            for each in data:
                if self.check_subscriber(each['Number']):
                    dictionary = {
                        'ID': each['Number'],
                        'Address': each['ПредставлениеАдреса'],
                        'Telephone': each['ФизическоеЛицо']['Телефон'],
                        'Name': each['ФизическоеЛицо']['Description'],
                        'Tv_number': each['ФизическоеЛицо']['КоличествоТВ'],
                        'Comment': each['ФизическоеЛицо']['Комментарий']
                    }
                    result.append(dictionary)
        if result and len(result) == 1:
            balance = self.get_balance(result[0]['ID'])
        if self.can_make_report(request.user):
            base_template = 'reports.html'
        else:
            base_template = 'index.html'
        context = {
            'search_data': search_data,
            'result': result,
            'balance': balance,
            'base_template': base_template
        }
        return render(request, template, context)

    def data_extractor(self, address):
        search_by = ''
        data = ['КварталМассив/Description eq ',
                ' and Дом/Description eq ',
                ' and Квартира/Description eq '
                ]
        eng = ['quarter', 'building', 'apartment']
        for each in range(len(address)):
            search_by = search_by + data[each] + '\'%s\'' % address[eng[each]]
        url = 'odata/standard.odata/' \
              'Document_АбонентскийДоговор?$format=json;odata=nometadata' \
              '&$select=Number,ПредставлениеАдреса,ФизическоеЛицо/Description,' \
              'ФизическоеЛицо/Телефон,ФизическоеЛицо/КоличествоТВ,' \
              'ФизическоеЛицо/Комментарий' \
              '&$filter=ВАрхиве eq false and %s' \
              '&$expand=ФизическоеЛицо' \
              '&$orderby=ПредставлениеАдреса asc' % search_by
        result = self.Connector(url).json()['value']
        return result

    def check_subscriber(self, uid):
        url = 'hs/payme/get/%s' % uid
        response = self.Connector(url)
        result = literal_eval(response.content.decode())
        return result

    def data_splitter(self, address):
        parameters = ['quarter', 'building', 'apartment']
        split_data = address.split('-')
        result = {}
        for each in range(len(split_data)):
            result[parameters[each]] = split_data[each]
        return result

    def get_balance(self, uid):
        url = 'hs/subjectinfo/%s' % uid
        balance = self.Connector(url).json()
        return balance

    def can_make_report(self, user):
        get_worker = Worker.objects.filter(user=user)
        if get_worker.__len__() > 0:
            return True
        return False
