from django.contrib import admin
from .models import WorkCalc, BonusWork, CategoryOfChange, Worker, AccountChange, Total, Work, WorkReport

# Register your models here.
class WorkReportAdmin(admin.ModelAdmin):
    list_display = ['working_date', 'user', 'quarter', 'apartment',
                    'building', 'work', 'cost', 'confirmed', 'deleted']

    date_hierarchy = 'working_date'

admin.site.register(WorkCalc)
admin.site.register(BonusWork)
admin.site.register(CategoryOfChange)
admin.site.register(Worker)
admin.site.register(AccountChange)
admin.site.register(Total)
admin.site.register(Work)
admin.site.register(WorkReport, WorkReportAdmin)