from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from basicauth.decorators import basic_auth_required
from django.views.decorators.csrf import csrf_exempt
import logging
import json

# Create your views here.
@method_decorator(basic_auth_required, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class RequestReceiver(View):

    def get(self, request):
        pass

    def post(self, request):
        logging.DEBUG(request.body.decode('utf-8', 'ignore'))
        try:
            json_data = json.loads(request.body.decode('utf-8', 'ignore'))
            result = {
                'result': 'ok',
                'data': json_data
            }
            logging.DEBUG(result)
            return JsonResponse(result)
        except:
            result = {
                'error': 'bad_request',
                'data': 'wrong_data'
            }
            logging.DEBUG(result)
            return JsonResponse(result)



