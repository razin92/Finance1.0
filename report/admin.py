from django.contrib import admin
from .models import BalanceStamp
# Register your models here.

class BalanceStampAdmin(admin.ModelAdmin):
    list_display = ('date', 'pouch', 'balance')

admin.site.register(BalanceStamp, BalanceStampAdmin)