from .models import Profile, ShippingDetails, PersonalDetails, PaymentDetails, Coupon, Subscription, Customer
from django.utils.html import escape, mark_safe
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib import admin
from django.urls import reverse



class CustomCustomerAdmin(admin.ModelAdmin):
    
    list_display = [field.name for field in Customer._meta.get_fields()]
    list_display_links = ['id']



class CustomSubscriptionAdmin(admin.ModelAdmin):
    
    list_display = [field.name for field in Subscription._meta.get_fields()]
    list_display_links = ['id']
    


class CustomCouponAdmin(admin.ModelAdmin):
    
    list_display = ('id', 'description', 'coupon_code', 'discount_dollars')
    list_display_links = ['id']
    
    def discount_dollars(self, instance):
        return instance.discount
    discount_dollars.short_description = 'Discount (Dollars)'



class CustomPaymentDetailsAdmin(admin.ModelAdmin):
    
    list_display = [field.name for field in PaymentDetails._meta.get_fields()]
    list_display_links = ['id']
    


class CustomShippingDetailsAdmin(admin.ModelAdmin):
    
    list_display = [field.name for field in ShippingDetails._meta.get_fields()]
    #list_display = ('get_email', 'address1', 'address2')

    def get_email(self, instance):
        return instance.email
    get_email.short_description = 'email'



class CustomPersonalDetailsAdmin(admin.ModelAdmin):
    
    list_display = [field.name for field in PersonalDetails._meta.get_fields()]
    list_display_links = ['id']
    
    

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'



class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )

    list_display = ('id', 'email', 'first_name', 'last_name')#, 'get_phone')
    list_select_related = ('profile', )
    list_display_links = ['id']

    def get_phone(self, instance):
        return instance.profile.personal_details.phone
    get_phone.short_description = 'Phone'
        
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)



admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(ShippingDetails, CustomShippingDetailsAdmin)
admin.site.register(PersonalDetails, CustomPersonalDetailsAdmin)
admin.site.register(PaymentDetails, CustomPaymentDetailsAdmin)
admin.site.register(Coupon, CustomCouponAdmin)
admin.site.register(Subscription, CustomSubscriptionAdmin)
admin.site.register(Customer, CustomCustomerAdmin)