from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views


app_name = 'lib'
urlpatterns = [
    #ex: /calc/
    url(r'^person/$', login_required(views.PersonView.as_view()), name='person'),
    url(r'^person/edit/(?P<pk>\d+)$', login_required(views.PersonEdit.as_view()), name='person_edit'),
    url(r'^person/create/$', login_required(views.PersonCreate.as_view()), name='person_create'),
    url(r'^person/delete/(?P<pk>\d+)$', login_required(views.PersonDelete.as_view()), name='person_delete'),
    url(r'^pouch/$', login_required(views.PouchView), name='pouch'),
    url(r'^pouch/edit/(?P<pk>\d+)$', login_required(views.PouchEdit.as_view()), name='pouch_edit'),
    url(r'^pouch/create/$', login_required(views.PouchCreate.as_view()), name='pouch_create'),
    url(r'^pouch/delete/(?P<pk>\d+)$', login_required(views.PouchDelete.as_view()), name='pouch_delete'),
    url(r'^category/$', login_required(views.CategoryView.as_view()), name='category'),
    url(r'^category/edit/(?P<pk>\d+)$', login_required(views.CategoryEdit.as_view()), name='category_edit'),
    url(r'^category/create/$', login_required(views.CategoryCreate.as_view()), name='category_create'),
    url(r'^category/delete/(?P<pk>\d+)$', login_required(views.CategoryDelete.as_view()), name='category_delete'),
    #url(r'^(?P<pk>[0-9]+)/$', views.TransactionDetailView.as_view(), name='transaction_detail'),
    #url(r'^(?P<transaction_id>[0-9]+)/change/$', views.changer, name='changer'),

    ]