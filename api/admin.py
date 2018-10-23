from django.contrib import admin
from .models import SubscriberRequest, Logging

# Register your models here.
class SubscriberRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'request_id', 'ops_date',
                    'request_status', 'request_work',
                    'request_address', 'worker']
    search_fields = ['id', 'request_address']

class LoggingAdmin(admin.ModelAdmin):
    list_display = ['id', 'request', 'request_status', 'request_result']
    search_fields = ['id']


admin.site.register(SubscriberRequest, SubscriberRequestAdmin)
admin.site.register(Logging, LoggingAdmin)