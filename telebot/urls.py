#from django.conf.urls import url
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'telebot'
urlpatterns = [
            url(r'^bot_start/$', login_required(views.run_bot), name='run_bot'),
        ]