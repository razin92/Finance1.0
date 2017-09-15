from django.contrib import admin
from .models import Person, Pouch, Category, Staff

class PersonAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'secondname')

class PouchAdmin(admin.ModelAdmin):
    list_display = ('name', 'balance', 'type')

admin.site.register(Person, PersonAdmin)
admin.site.register(Pouch, PouchAdmin)
admin.site.register(Category)
admin.site.register(Staff)