from django.contrib import admin
from .models import BalanceStamp, TransactionChangeHistory
# Register your models here.

class BalanceStampAdmin(admin.ModelAdmin):
    list_display = ('date', 'pouch', 'balance_before', 'balance_after')

class TransactionChangeHistoryAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'date_before', 'date_after', 'sum_val_before', 'sum_val_after',
'category_before', 'category_after', 'who_is_before', 'who_is_after', 'comment_before', 'comment_after',
'money_before', 'money_after', 'date_of_create', 'date_of_change', 'creator', 'changer')

admin.site.register(BalanceStamp, BalanceStampAdmin)
admin.site.register(TransactionChangeHistory, TransactionChangeHistoryAdmin)