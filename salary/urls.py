from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views


app_name = 'salary'
urlpatterns = [
        url(r'^worker/$', login_required(views.WorkerView.as_view()), name='worker'),
        url(r'^worker/create/$', login_required(views.WorkerCreate.as_view()), name='worker_create'),

        url(r'^calc/$', login_required(views.WorkCalcView.as_view()), name='workcalc'),
        url(r'^calc/create/$', login_required(views.WorkCalcCreate.as_view()), name='workcalc_create'),

        url(r'^bonus/$', login_required(views.BonusWorkView.as_view()), name='bonuswork'),
        url(r'^bonus/mass/create/$', login_required(views.MassBonus.as_view()), name='mass_bonuswork'),
        url(r'^bonus/create/$', login_required(views.BonusWorkCreate), name='bonuswork_create'),
        url(r'^bonus/edit/(?P<pk>[0-9]+)$', login_required(views.BonusWorkEdit.as_view()), name='bonuswork_edit'),

        url(r'^category/$', login_required(views.CategoryOfChangeView.as_view()), name='categoryofchange'),
        url(r'^category/create/$', login_required(views.CategoryOfChangeCreate.as_view()), name='categoryofchange_create'),

        url(r'^changeacc/$', login_required(views.AccountChangeView.as_view()), name='accountchange'),
        url(r'^changeacc/create/$', login_required(views.AccountChangeCreate), name='accountchange_create'),
        url(r'^changeacc/edit/(?P<pk>[0-9]+)$', login_required(views.AccountChangeEdit.as_view()), name='accountchange_edit'),

        url(r'^total/$', login_required(views.TotalView), name='total'),
        url(r'^total/create/$', login_required(views.TotalCreate), name='total_create'),
        url(r'^total/get_salary/$', login_required(views.get_salary), name='get_salary'),

        url(r'^total/calculate/([1-2])/$', views.calculate, name='calculate'),
        url(r'^total/work_detail/(?P<worker_id>[0-9]+)$', views.accrual, name='accrual'),
        url(r'^total/bonus_detail/(?P<worker_id>[0-9]+)/(?P<total_id>[0-9]+)$', views.bonus, name='bonus'),
        url(r'^total/withholding_detail/(?P<worker_id>[0-9]+)/(?P<total_id>[0-9]+)$', views.withholding, name='withholding'),
        url(r'^total/issued_detail/(?P<worker_id>[0-9]+)/(?P<total_id>[0-9]+)$', views.issued, name='issued'),
        # Work reports
        url(r'^work_report/create/$', login_required(views.WorkerReportUser.as_view()), name='work_report_create'),
        url(r'^work_report/edit/$', login_required(views.WorkerReportUserEdit), name='work_report_edit'),
        url(r'^work/$', login_required(views.WorkView.as_view()), name='work'),
        url(r'^my_reports_list/(?P<page>[0-9]+)/$', login_required(views.MyWorkList.as_view()), name='my_reports_list'),
        url(r'^reports_list/$', login_required(views.ReportsList.as_view()), name='reports_list'),
        url(r'^reports_history/$', login_required(views.ReportHistory.as_view()), name='reports_history'),
        url(r'^detailed_report/$', login_required(views.ConsolidatedReport.as_view()), name='detailed_report'),
        url(r'^report_confirm/$', login_required(views.ReportConfirmation.as_view()), name='report_confirm'),
        # Searching
        url(r'^search/$', login_required(views.SubsSearcher.as_view()), name='subscriber_search'),
        ]