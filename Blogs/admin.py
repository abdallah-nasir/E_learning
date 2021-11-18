from django.contrib import admin
from .models import *
# Register your models here.
class BlogAdmin(admin.ModelAdmin):
    list_display=["name","paid"]
admin.site.register(Blog,BlogAdmin)
admin.site.register(Blog_Comment)
admin.site.register(Blog_Comment_Reply)
admin.site.register(Blog_Views)
admin.site.register(Category)
admin.site.register(Blog_Images)
admin.site.register(Blog_Payment)
admin.site.register(Prices)



    