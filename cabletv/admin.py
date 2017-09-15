from django.contrib import admin
from .models import (
    CableTvType, CableTvQuarter,  CableTvDistrict, CableTvZone,
    CableTvPouch, CableTvSource, CableTvResult, CableTvCat
)

admin.site.register(CableTvZone)
admin.site.register(CableTvCat)
admin.site.register(CableTvResult)
admin.site.register(CableTvDistrict)
admin.site.register(CableTvQuarter)
admin.site.register(CableTvType)
admin.site.register(CableTvPouch)
admin.site.register(CableTvSource)