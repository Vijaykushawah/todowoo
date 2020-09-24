from django.contrib import admin
from .models import Todo,Contact,MyProfile
# Register your models here.
class TodoAdmin(admin.ModelAdmin):
    readonly_fields=['created',]


admin.site.register(Todo,TodoAdmin)
admin.site.register(Contact)
admin.site.register(MyProfile)
