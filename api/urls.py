from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views import RequestReceiver, StatusChanger, StatusChangeTest, NewJobsList


app_name = 'api'
urlpatterns = [
    url(r'^new_request/$', RequestReceiver.as_view(), name='create'),
    url(r'^update_request/$', StatusChanger.as_view(), name='change'),
    url(r'^test/$', StatusChangeTest.as_view(), name='test'),
    url(r'^new_jobs/$', NewJobsList.as_view(), name='new_jobs')
]