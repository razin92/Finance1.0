from django.test import TestCase
import requests

# Create your tests here.
class RequestTest(TestCase):

    def make_request(self):
        url = 'http://127.0.0.1:8000/'
        uri = 'api/new_request/'
        login = 'testuser'
        password = 'Password156324'
        request = {
            'ref_key': '1d00365d-d6ac-11e8-add5-b870f4a63fc5',
            'ops_date': '23.10.2018 15:12:06',
            'rqst_id': '000015778',
            'rqsted_work': 'не показ',
            'rqst_address': '6-35-70'
        }
        r = requests.post(
            url+uri, json=request, auth=(login, password)
        )
        print(r.status_code)
        if r.status_code == 200:
            print(r.json())