from django.contrib import admin
from .models import BalanceStamp, TransactionChangeHistory
# Register your models here.

class BalanceStampAdmin(admin.ModelAdmin):
    list_display = ('date', 'pouch', 'balance')

admin.site.register(BalanceStamp, BalanceStampAdmin)
admin.site.register(TransactionChangeHistory)