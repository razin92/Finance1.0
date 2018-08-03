from django import template

register = template.Library()

@register.filter(name='dictionary')
def dictionary(data):
    translate = ['Квартал: ', ', Дом: ', ', Квартира: ']
    eng = ['quarter', 'building', 'apartment']
    result = ''
    for each in range(len(data)):
        result = result + translate[each] + data[eng[each]]
    return result


@register.filter(name='get_key')
def get_key(key, value):
    result = key[value]
    return result