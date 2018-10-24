from django.shortcuts import render, reverse
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from basicauth.decorators import basic_auth_required
from django.views.decorators.csrf import csrf_exempt
from salary.models import Worker
from django.db import DatabaseError
from .models import SubscriberRequest
from .forms import StatusChangingForm
import requests
import datetime
import logging
import json

logging = logging.getLogger(__name__)


# Create your views here.
@method_decorator(basic_auth_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class RequestReceiver(View):

    def get(self, request):
        pass

    def post(self, request):
        body = json.loads(request.body.decode('utf-8', 'ignore'))
        logging.debug(body)
        created = self.create_request(body)
        return JsonResponse(created)

    def create_request(self, body):
        try:
            new_request = SubscriberRequest.objects.create(
                request_id=body['rqst_id'],
                ref_key=body['ref_key'],
                ops_date=datetime.datetime.strptime(body['ops_date'], '%d.%m.%Y %H:%M:%S'),
                request_work=body['rqsted_work'],
                request_address=body['rqst_address'],
                request_comment=body['rqst_comment']
            )
            logging.debug('%s %s' % (new_request, 'created'))
            return {'result': 'ok'}
        except DatabaseError:
            return {'result': 'already exists'}


@method_decorator(basic_auth_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class StatusChanger(View):

    def post(self, request):
        body = json.loads(request.body.decode('utf-8', 'ignore'))
        logging.debug(body)
        result = self.change_status(body)
        return JsonResponse(result)

    def change_status(self, data):
        try:
            request = SubscriberRequest.objects.get(
                ref_key=data['ref_key']
            )
            request.request_status = data['rqst_status']
            request.request_comment = request.request_comment + ' %s' % data['rqst_comment']
            if data['master_ref_key']:
                request.worker = Worker.objects.get(one_c_worker_name=data['master_ref_key'])
            request.save()
            return {'result': 'ok'}
        except DatabaseError:
            logging.debug('%s not found' % data['ref_key'])
            return {'result': 'not found'}


class StatusChangeTest(View):

    template = 'status_changer.html'

    def get(self, request):
        form = StatusChangingForm(None)
        return render(request, self.template, context={'form': form})

    def post(self, request):
        post = request.POST
        form = StatusChangingForm(post)
        result = None
        if form.is_valid():
            url = post['target']
            login = 'testuser'
            password = 'Password156324'
            JSON = {
                'ops_date': datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S'),
                'ref_key': SubscriberRequest.objects.get(id=post['request']).ref_key,
                'rqst_status': post['status'],
                'rqst_comment': post['comment'],
                'master_ref_key': post['master']
            }
            r = requests.post(
                url, json=JSON, auth=(login, password)
            )
            result = {'status': r.status_code, 'json': JSON}
            if result['status'] == 200:
                try:
                    result['status'] = r.json()
                except:
                    pass

        return render(request, self.template, context={'form': form, 'result': result})