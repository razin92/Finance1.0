from django import template
from django.db.models import Sum

register = template.Library()
@register.filter(name='salary')
def salary(salary):
    result = salary.aggregate(Sum('cost'))['cost__sum']
    return result