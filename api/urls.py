from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views import RequestReceiver


app_name = 'api'
urlpatterns = [
    url(r'^new_request/$', RequestReceiver.as_view())
]