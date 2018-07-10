from django import template
from ..models import Worker
from django.db.models import Sum

register = template.Library()

@register.filter(name='value')
def value(value, arg):
    result = getattr(value, arg)
    if arg == 'working_date':
        return result.strftime('%m-%d')
    elif arg == 'confirmed':
        if result:
            return 'Принята'
        return 'Не принята'
    elif arg == 'coworker':
        values = [x.name.firstname for x in result.all()]
        if len(values) > 0:
            return ', '.join(values)
        return ''
    elif arg == 'user':
        user = Worker.objects.filter(user=result)
        if user.__len__() > 0:
            return user[0].name
    elif arg == 'deleted':
        if result == True:
            return 'УДАЛЕНО'
    elif arg == 'apartment':
        if not result:
            return '--'
        
    return result


@register.filter(name='salary')
def salary(salary):
    result = salary.aggregate(Sum('cost'))['cost__sum']
    return result
