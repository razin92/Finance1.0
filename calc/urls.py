from django.conf.urls import url
from .views import TransactionView, TransactionDetailView, changer, TransactionCreate, calculate
from django.contrib.auth.decorators import login_required



app_name = 'calc'
urlpatterns = [
    #ex: /calc/
    url(r'^transactions/$', TransactionView, name='transaction'),
    url(r'^transactions/page/(?P<page>\d+)/$', TransactionView, name='transaction_page'),
    url(r'^transactions/(?P<pk>[0-9]+)/$', TransactionDetailView, name='transaction_detail'),
    url(r'^transactions/(?P<transaction_id>[0-9]+)/change/$', changer, name='changer'),
    url(r'^transactions/create/([0-1]+)/$', login_required(TransactionCreate), name='transaction_create'),
    url(r'^transactions/calc/([0-1]+)/$', calculate, name='transaction_calc'),
    ]