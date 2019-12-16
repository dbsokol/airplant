from django.db import models



class Subscription_archive(models.Model):
    
    ''' Subscriptions table '''

    user = models.CharField(max_length=200, default=None, blank=True, null=True)
    braintree_subscription_id = models.CharField(max_length=200, default=None, blank=True, null=True)
    subscription_name = models.CharField(max_length=100, default=None, blank=True, null=True)
    shipping_details = models.TextField(default=None, blank=True, null=True)
    start_date = models.DateField(default=None, blank=True, null=True)
    end_date = models.DateField(default=None, blank=True, null=True)
    number_of_months = models.IntegerField(default=None, blank=True, null=True)
    reason_for_canceling = models.TextField(default=None, blank=True, null=True)
    