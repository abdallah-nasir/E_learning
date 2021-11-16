from django.contrib import admin
from .models import *
# Register your models here.

class PaymentAdmin(admin.ModelAdmin):
    list_display=("method","ordered")

admin.site.register(Branch)
admin.site.register(Category)
admin.site.register(Videos)
admin.site.register(Course)
admin.site.register(Reviews)
admin.site.register(Events)
admin.site.register(Wishlist)
admin.site.register(Blog)
admin.site.register(Blog_Comment)
admin.site.register(Blog_Comment_Reply)
admin.site.register(Teacher_review)
admin.site.register(Blog_Views)
admin.site.register(Payment,PaymentAdmin)




