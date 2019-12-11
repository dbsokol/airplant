from django.db.models.signals import post_save
from django.contrib.auth.models import User, AbstractUser, BaseUserManager
from django.dispatch import receiver
from django.db import models



class PersonalDetails(models.Model):
    
    ''' Personal Details table '''
    
    email = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    
    def __str__(self):
        return self.email
        
    class Meta:
        verbose_name = 'Personal Details'
        verbose_name_plural = 'Personal Details'
        
    
    
class ShippingDetails(models.Model):
    
    ''' Shipping Details table '''
    
    email = models.CharField(max_length=100, default=None, blank=True, null=True) 
    first_name = models.CharField(max_length=100, default=None, blank=True, null=True)
    last_name = models.CharField(max_length=100, default=None, blank=True, null=True)
    address1 = models.CharField(max_length=100, default=None, blank=True, null=True)
    address2 = models.CharField(max_length=100, default=None, blank=True, null=True)
    country = models.CharField(max_length=100, default=None, blank=True, null=True)
    state = models.CharField(max_length=100, default=None, blank=True, null=True)
    zip_code = models.CharField(max_length=100, default=None, blank=True, null=True)
    city = models.CharField(max_length=100, default=None, blank=True, null=True)
    street_name = models.CharField(max_length=100, default=None, blank=True, null=True)
    street_number = models.CharField(max_length=100, default=None, blank=True, null=True)
    
    def __str__(self):
        return self.email
        
    class Meta:
        verbose_name = 'Shipping Details'
        verbose_name_plural = 'Shipping Details'



class PaymentDetails(models.Model):
    
    ''' Payment Details table '''
    
    email = models.CharField(max_length=100, default=None, blank=True, null=True) 
    payment_token = models.CharField(max_length=5000, default=None, blank=True, null=True)
    card_type = models.CharField(max_length=100, default=None, blank=True, null=True)
    last_four = models.IntegerField(default=None, blank=True, null=True)
    expiration = models.CharField(max_length=100, default=None, blank=True, null=True)
    start_date = models.DateField(default=None, blank=True, null=True)
    
    def __str__(self):
        return self.email
        
    class Meta:
        verbose_name = 'Payment Details'
        verbose_name_plural = 'Payment Details'
        
      
      
class Coupon(models.Model):
    
    ''' Coupons table '''
    
    description = models.CharField(max_length=100, default=None, blank=True, null=True)
    coupon_code = models.CharField(max_length=100, default=None, blank=True, null=True)
    discount = models.CharField(max_length=100, default=None, blank=True, null=True)
    
    def __str__(self):
        return self.description
        
        

class Subscription(models.Model):
    
    ''' Subscriptions table '''

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription_name = models.CharField(max_length=100, default=None, blank=True, null=True)
    address_details = models.OneToOneField(ShippingDetails, on_delete=models.CASCADE)
    start_date = models.DateField(default=None, blank=True, null=True)
    end_date = models.DateField(default=None, blank=True, null=True)
    number_of_months = models.IntegerField(default=None, blank=True, null=True)
    activte_status = models.BooleanField(default=False)
    continue_status = models.BooleanField(default=False)
    qued_status = models.BooleanField(default=False)
    fulfilled_status = models.BooleanField(default=False)
    gift_status = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.email


        
class Profile(models.Model):
    
    ''' Extedned django user class '''
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    personal_details = models.OneToOneField(PersonalDetails, on_delete=models.CASCADE, default=None, blank=True, null=True)
    shipping_details = models.OneToOneField(ShippingDetails, on_delete=models.CASCADE, default=None, blank=True, null=True)
    payment_details = models.OneToOneField(PaymentDetails, on_delete=models.CASCADE, default=None, blank=True, null=True)
   
    def __str__(self):
        return self.user.email
   
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()