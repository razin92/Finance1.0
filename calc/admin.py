from django.contrib import admin
from .models import Transaction

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'sum_val', 'category', 'who_is', 'comment', 'money', 'checking', 'typeof', 'creator', 'create_date')

admin.site.register(Transaction, TransactionAdmin)