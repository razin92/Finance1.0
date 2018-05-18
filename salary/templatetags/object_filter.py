from django import template

register = template.Library()

@register.filter(name='value')
def value(value, arg):
    result = getattr(value, arg)
    if arg == 'working_date':
        return result.strftime('%m-%d')
    elif arg == 'confirmed':
        if result:
            return 'Принята'
        return 'НЕ принята'
    elif arg == 'coworker':
        values = [x.name.firstname for x in result.all()]
        if len(values) > 0:
            return ', '.join(values)
        return ''
    return result