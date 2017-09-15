from django.contrib import admin
from .models import WorkCalc, BonusWork, CategoryOfChange, Worker, AccountChange, Total

# Register your models here.
admin.site.register(WorkCalc)
admin.site.register(BonusWork)
admin.site.register(CategoryOfChange)
admin.site.register(Worker)
admin.site.register(AccountChange)
admin.site.register(Total)