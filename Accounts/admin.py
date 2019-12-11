from .models import Profile, ShippingDetails, PersonalDetails, PaymentDetails, Coupon, Subscription
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib import admin



class CustomScubscriptionAdmin(admin.ModelAdmin):
    
    list_display = ('get_email', 'subscription_name')
    
    def get_email(self, instance):
        return instance.user.email
    get_email.short_description = 'email'
    
    

class CustomCouponAdmin(admin.ModelAdmin):
    
    list_display = ('description', 'coupon_code', 'discount')
    



class CustomPaymentDetailsAdmin(admin.ModelAdmin):
    
    list_display = ('pk', 'get_email', 'card_type', 'last_four',)

    def get_email(self, instance):
        return instance.email
    get_email.short_description = 'email'



class CustomShippingDetailsAdmin(admin.ModelAdmin):
    
    list_display = ('get_email', 'address1', 'address2')

    def get_email(self, instance):
        return instance.email
    get_email.short_description = 'email'



class CustomPersonalDetailsAdmin(admin.ModelAdmin):
    
    list_display = ('email', 'first_name', 'last_name', 'phone')
    
    

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'



class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )

    list_display = ('email', 'first_name', 'last_name')#, 'get_phone')
    list_select_related = ('profile', )

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
admin.site.register(Subscription, CustomScubscriptionAdmin)