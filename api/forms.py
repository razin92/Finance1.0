from django.forms import Form, ModelChoiceField, ChoiceField, CharField, Textarea
from .models import SubscriberRequest, Lib
from salary.models import Worker

class StatusChangingForm(Form):

    targets = (
        ('https://mng.pst.uz:88/api/update_request/', 'Django'),
        ('http://192.168.220.30/TESTBASE/hs/apidjango/post/', '1C')
    )

    target = ChoiceField(choices=targets, label='Цель запроса')
    request = ModelChoiceField(queryset=SubscriberRequest.objects.all(), label='Заявка ID-Работа-Статус в Django')
    status = ChoiceField(choices=Lib().statuses(), label='Статус на изменение')
    comment = CharField(max_length=255, required=False, label='Комментарий', widget=Textarea(
        attrs={'rows': '4', 'maxlength': '255'}
    ))
    master = ChoiceField(label='Мастер из базы Django', choices=(
        (x.one_c_worker_name, x) for x in Worker.objects.filter(one_c_worker_name__isnull=False)),
        required=False
    )