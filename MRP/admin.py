from django.contrib import admin
from .models import *

# Register your models here.


admin.site.register(Chemical)
admin.site.register(Vendor)
admin.site.register(PO)
admin.site.register(Inv_PO)
admin.site.register(WeekLoading)
admin.site.register(Inv_Chemical)
admin.site.register(Package)
admin.site.register(Status_Chem)
#admin.site.register(ShowStatus)
admin.site.register(EoqBoqload)