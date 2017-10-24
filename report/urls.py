from django.conf.urls import url
from . import views


app_name = 'report'
urlpatterns = [
        url(r'^transaction/$', views.report_transaction, name='report_transaction'),
        url(r'^transaction/filter-result/$', views.report_transaction_filter, name='transaction_filter'),

        url(r'^workers/$', views.report_workers, name='report_workers'),
        url(r'^workers/filter/$', views.report_workers_filter, name='workers_filter'),

        url(r'^stamp/$', views.balance_freezer, name='freeze'),

        ]