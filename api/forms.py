from django.forms import Form, ModelChoiceField, ChoiceField, CharField, Textarea
from .models import SubscriberRequest, Lib

class StatusChangingForm(Form):

    request = ModelChoiceField(queryset=SubscriberRequest.objects.all())
    status = ChoiceField(choices=Lib().statuses())
    comment = CharField(max_length=255, required=False, widget=Textarea(
        attrs={'rows': '4', 'maxlength': '255'}
    ))