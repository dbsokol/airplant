from .models import Subscription_archive
from django.contrib import admin



class CustomSubscriptionArchiveAdmin(admin.ModelAdmin):
    
    list_display = [field.name for field in Subscription_archive._meta.get_fields()]
    #list_display = ('get_email', 'subscription_name')
    list_display_links = ['id']
    
    
admin.site.register(Subscription_archive, CustomSubscriptionArchiveAdmin)