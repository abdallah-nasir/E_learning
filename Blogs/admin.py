from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Blog)
admin.site.register(Blog_Comment)
admin.site.register(Blog_Comment_Reply)
admin.site.register(Blog_Views)
admin.site.register(Category)
admin.site.register(Blog_Images)
admin.site.register(Blog_Payment)
admin.site.register(Prices)



    