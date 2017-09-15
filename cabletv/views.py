from django.shortcuts import render
from django.views import generic
from .models import CableTvResult
from django.core.urlresolvers import reverse_lazy
# Create your views here.
class CableTvResultView(generic.ListView):
    template_name = 'cabletv/result.html'
    context_object_name = 'result'

    def get_queryset(self):
        return CableTvResult.objects.order_by('date_year')

class CableTvResultCreate(generic.CreateView):
    model = CableTvResult
    template_name = 'cabletv/result_create.html'
    success_url = reverse_lazy('cabletv:result')
    fields = ['date_year', 'date_month', 'sum', 'account', 'comment']