from django.contrib import admin
from .models import WorkCalc, BonusWork, CategoryOfChange, Worker, AccountChange, Total, Work, WorkReport

# Register your models here.
class WorkReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'working_date', 'user', 'quarter', 'building',
                    'apartment','work', 'cost', 'confirmed', 'deleted']

    date_hierarchy = 'working_date'
    search_fields = ['id']

class TotalAdmin(admin.ModelAdmin):
    list_display = ['date', 'worker', 'balance_before', 'balance_now']

admin.site.register(WorkCalc)
admin.site.register(BonusWork)
admin.site.register(CategoryOfChange)
admin.site.register(Worker)
admin.site.register(AccountChange)
admin.site.register(Total, TotalAdmin)
admin.site.register(Work)
admin.site.register(WorkReport, WorkReportAdmin)