from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views


app_name = 'cabletv'
urlpatterns = [
    url(r'^$', login_required(views.CableTvResultView.as_view()), name='result'),
    url(r'^create/$', login_required(views.CableTvResultCreate.as_view()), name='result_create'),
        ]
