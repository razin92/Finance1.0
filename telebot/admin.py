from django.contrib import admin
from .models import AuthorizedUser, Schedule
# Register your models here.

class AuthorizedUserAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'secondname', 'user_name', 'user_id', 'telephone')

class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('name', 'master', 'date_start', 'accepted')

admin.site.register(AuthorizedUser, AuthorizedUserAdmin)
admin.site.register(Schedule, ScheduleAdmin)