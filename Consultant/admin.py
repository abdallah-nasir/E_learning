from django.contrib import admin
from .models import *
# Register your models here.
class ConsultantAdmin(admin.ModelAdmin):
    list_display=["id","pending","completed"]

class ConsultantPaymentAdmin(admin.ModelAdmin):
    list_display=["method","id","pending","ordered"]
admin.site.register(Category)
admin.site.register(Teacher_Time)
admin.site.register(Consultant,ConsultantAdmin)
admin.site.register(Cosultant_Payment,ConsultantPaymentAdmin)