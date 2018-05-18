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

        url(r'^total/calculate/([0-9]{1})/$', views.calculate, name='calculate'),
        url(r'^total/work_detail/(?P<worker_id>[0-9]+)$', views.accrual, name='accrual'),
        url(r'^total/bonus_detail/(?P<worker_id>[0-9]+)/(?P<total_id>[0-9]+)$', views.bonus, name='bonus'),
        url(r'^total/withholding_detail/(?P<worker_id>[0-9]+)/(?P<total_id>[0-9]+)$', views.withholding, name='withholding'),
        url(r'^total/issued_detail/(?P<worker_id>[0-9]+)/(?P<total_id>[0-9]+)$', views.issued, name='issued'),

        url(r'^work_report/create/$', views.WorkerReportUser.as_view(), name='work_report_create'),
        url(r'^work/$', views.WorkView.as_view(), name='work'),
        url(r'^work_reports_list/$', views.WorkList.as_view(), name='work_reports_list')
        ]