from django.contrib import admin
from .models import Todo,Contact,MyProfile,SendMultiMail
# Register your models here.
class TodoAdmin(admin.ModelAdmin):
    readonly_fields=['created',]

class SendMultiMailAdmin(admin.ModelAdmin):
    readonly_fields=['created',]

admin.site.register(Todo,TodoAdmin)
admin.site.register(Contact)
admin.site.register(MyProfile)
admin.site.register(SendMultiMail,SendMultiMailAdmin)
