from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from basicauth.decorators import basic_auth_required
from django.views.decorators.csrf import csrf_exempt
from django.db import DatabaseError
from .models import SubscriberRequest
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
                request_address=body['rqst_address']
            )
            logging.debug('%s %s' % (new_request, 'created'))
            return {'result': 'ok'}
        except DatabaseError:
            return {'result': 'already exists'}
