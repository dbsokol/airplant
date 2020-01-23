from Accounts.models import Subscription, User, PersonalDetails, ShippingDetails, PaymentDetails
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth.decorators import login_required
from datetime import datetime, timezone, timedelta, date
from django.views.decorators.csrf import csrf_exempt
from .models import Subscription_archive
import Backend.BackendFunctions as funcs
from airplant.settings import gateway
from django.http import HttpResponse
import Tools.Tools as tools
from time import time
import traceback
import hashlib
import json



@login_required(login_url='')
def Profile(request):
    
    ''' Accepts request from '/profile', renders profile.html template '''

    tools.PrintTitle('Backend.views.Profile')
    
    try:
        
        # debug:
        print('[Backend.views.Profile]: Got post request with [%s]' %request.POST)
        
        user = request.user
        context = {
        'personal_details' : user.profile.personal_details,
        'payment_details' : user.profile.payment_details,
        'shipping_details' : user.profile.shipping_details,
        'subscription' : user.profile.subscription,
        }
        
        status = 0
        message = 'Edit your Profile.'
        internal_message = ''
    
    except Exception as error:
        
        context = {'none' : 'none'}
        status = 1
        message = 'Unable to load your Profile.'
        internal_message = traceback.format_exc()
        
    print('[Backend.views.Profile]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message)) 
    
    return render(request, 'profile.html', context=context)



def CancelSubscription(request):
    
    ''' Accepts request to /cancel_subscription, cancels subscription and updates database '''
    
    tools.PrintTitle('Backend.views.CancelSubscription')
    
    try:
        
        # debug:
        print('[Backend.views.CancelSubscription]: Got post request with [%s]' %request.POST)
        
        # unpack post request:
        user = request.user
        reason_for_canceling = request.POST.getlist('reason_for_canceling[]')
        
        # get subsctiption object:
        subscription = user.profile.subscription
        braintree_subscription_id = subscription.braintree_subscription_id
    
        # cancel subscription:
        result = gateway.subscription.cancel(braintree_subscription_id)
        
        # udpate subscription object:
        subscription.active_status = False
        subscription.end_date = datetime.now(timezone.utc)
        subscription.reason_for_canceling = str(reason_for_canceling)
        subscription.save()
        
        # subscription_archive keywords:
        subscription_archive_kwargs = {
            'user' : user.profile.personal_details.email,
            'braintree_subscription_id' : braintree_subscription_id,
            'subscription_name' : subscription.subscription_name,
            'shipping_details' : user.profile.shipping_details.address1 + ' ' + user.profile.shipping_details.address2,
            'start_date' : subscription.start_date,
            'end_date' : subscription.end_date, 
            'next_billing_date' : subscription.next_billing_date,
            'billing_day_of_month' : subscription.billing_day_of_month,
            'number_of_months' : (subscription.end_date.year - subscription.start_date.year) * 12 + subscription.end_date.month - subscription.start_date.month,
            'reason_for_canceling' : reason_for_canceling,
        }
        
        # archive subscription:
        Subscription_archive.objects.create(**subscription_archive_kwargs)
        
        # debug:
        print('[Backend.views.CancelSubscription]: Canceled braintree subscription with [BraintreeResult:%s]' %result.is_success)
        
        status = 0
        message = 'You have successfully cancelled your subscription.'
        internal_message = message
        
    except Exception as error:
        
        status = 1
        message = 'There was an error when trying to cancel your subscription, please contact support@airplant.garden for assistance.'
        internal_message = traceback.format_exc()
        
    print('[Backend.views.CancelSubscription]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message)) 
    
    return HttpResponse(json.dumps({'status' : status, 'message' : message}))

    
    
def ReactivateSubscription(request):
    
    ''' Accepts request to /reactivate_subscription, reactivates subscription and updates database '''
    
    tools.PrintTitle('Backend.views.ReactivateSubscription')
    
    try:
        
        # debug:
        print('[Backend.views.ReactivateSubscription]: Got post request with [%s]' %request.POST)
        
        # unpack post request:
        user = request.user
        
        # get payment_details, subscription archive objects:
        payment_details = user.profile.payment_details
        subscription = user.profile.subscription
        
        # get count of archived subscriptions:
        count = Subscription_archive.objects.filter(user=user.email).count()
        
        new_subscription_id = 's_' + str(count).zfill(4) + subscription.braintree_subscription_id[6:]
        
        # get subscription object keywords:
        subscription_kwargs = {
            'email' : request.POST['email'],
            'braintree_subscription_id' : new_subscription_id,
            'subscription_name' : 'Standard_Plan',
            'start_date' : datetime.now(timezone.utc),
            'next_billing_date' : None, # filled in later
            'billing_day_of_month' : None, # filled in later
            'active_status' : True,
            'continue_status' : True,
            'qued_status' : False,
            'fulfilled_status' : False,
            'gift_status' : False,
        }
        
        # determine next billing date:
        if subscription.next_billing_date < date.today():
            first_billing_date = date.today()
        else:
            first_billing_date = subscription.next_billing_date
        
        braintree_subscription_kwargs = {
            'id' : subscription_kwargs['braintree_subscription_id'],
            'payment_method_token' : payment_details.braintree_payment_method_token, 
            'plan_id' : 'Standard_Plan',
            'first_billing_date' : first_billing_date,
        }
        
        # create new braintree subscription:
        braintree_subscription_result = gateway.subscription.create(braintree_subscription_kwargs)
        
        # delete subscription object:
        subscription.delete()
       
        # create new subscription object:
        subscription_kwargs['next_billing_date'] = braintree_subscription_result.subscription.next_billing_date
        subscription_kwargs['billing_day_of_month'] = braintree_subscription_result.subscription.billing_day_of_month
        subscription = Subscription.objects.create(**subscription_kwargs)
        subscription.save()
        
        # register subscription to user:
        user.profile.subscription = subscription
        user.save()
        
        status = 0
        message = 'You have successfully reactivated your subscription, you will be billed on the [%s].' %first_billing_date
        internal_message = message
        
    except Exception as error:
        
        status = 1
        message = 'There was an error when trying to reactivate your subscription, please contact support@airplant.garden for assistance.'
        internal_message = traceback.format_exc()
        
    print('[Backend.views.ReactivateSubscription]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message)) 
    
    return HttpResponse(json.dumps({'status' : status, 'message' : message}))



def ChangePayment(request):
    
    ''' Accepts request /change_payment, changes the payment '''
    
    tools.PrintTitle('Backend.views.ChangePayment')
    
    try:
        
        # debug:
        print('[Backend.views.ChangePayment]: Got post request with [%s]' %request.POST)
        
        # unpack request:
        user = request.user
        last_four = request.POST['last_four']
        card_holder_name = request.POST['card_name']
        card_type = request.POST['card_type']
        expiration = request.POST['expiration']
        braintree_nonce = request.POST['nonce']

        # get payment details, subscription objects:
        payment_details = user.profile.payment_details
        subscription = user.profile.subscription

        # set payment_method key word arguments:
        payment_method_kwargs = {
            'customer_id' : 'c_' + hashlib.md5((request.POST['email'] + str(time())).encode('utf-8')).hexdigest(),
            'payment_method_nonce' : request.POST['nonce'],
        }

        # update braintree payment method object:
        braintree_payment_method_result = gateway.payment_method.update(
            payment_details.braintree_payment_method_token,
            {'payment_method_nonce' : request.POST['nonce'],}
        )

        # debug:
        if not braintree_payment_method_result.is_success:
            print('[Backend.views.ChangePayment]: Braintree error on payment method create [%s]' %braintree_payment_method_result)
        
        # update payment method in braintree subscription object:
        braintree_subscription_result = gateway.subscription.update(
            subscription.braintree_subscription_id, 
            {'payment_method_token': braintree_payment_method_result.payment_method.token,}
        )

        if not braintree_subscription_result.is_success:
            print('[Backend.views.ChangePayment]: Created braintree subscrption with [BraintreeResult:%s]' %braintree_subscription_result)

        # update payment details object:
        payment_details.braintree_payment_method_token = braintree_payment_method_result.payment_method.token
        payment_details.braintree_payment_method_global_id = braintree_payment_method_result.payment_method.global_id
        payment_details.customer_id = braintree_payment_method_result.payment_method.customer_id
        payment_details.card_holder_name = card_holder_name
        payment_details.last_four = last_four
        payment_details.card_type = card_type
        payment_details.expiration = expiration
        payment_details.save()

        status = 0
        message = 'Successfully updated your payment information.'
        internal_message = message
    
    except Exception as error:
        
        status = 1
        message = 'Unable to update your payment information, contact support@airplant.garden for assistance.'
        internal_message = traceback.format_exc()
        
    print('[Backend.views.ChangePayment]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message)) 
    
    return HttpResponse(json.dumps({'status' : status, 'message' : message}))



def ChangeShipping(request):
    
    ''' Accepts request /change_payment, changes the payment '''
    
    tools.PrintTitle('Backend.views.ChangeShipping')
    
    try:
        
        # debug:
        print('[Backend.views.ChangeShipping]: Got post request with [%s]' %request.POST)
        
        # unpack post request:
        user = request.user
        
        # get shipping details key word arguments from front end:
        shipping_details_kwargs = {
            'email' : request.POST['email'],
            'address1' : request.POST['address1'],
            'address2' : request.POST['address2'],
            'first_name' : request.POST['first_name'].capitalize(),
            'last_name' : request.POST['last_name'].capitalize(),
            'country' : request.POST['country'],
            'state' : request.POST['state'],
            'zip_code' : request.POST['zip_code'],
            'city' : request.POST['city'],
            'street_name' : request.POST['street_name'],
            'street_number' : request.POST['street_number'],     
        }
        
        # get payment details object:
        shipping_details = user.profile.shipping_details
        
        # update shipping details object:
        shipping_details.email = shipping_details_kwargs['email']
        shipping_details.first_name = shipping_details_kwargs['first_name']
        shipping_details.last_name = shipping_details_kwargs['last_name']
        shipping_details.address1 = shipping_details_kwargs['address1']
        shipping_details.address2 = shipping_details_kwargs['address2']
        shipping_details.country = shipping_details_kwargs['country']
        shipping_details.state = shipping_details_kwargs['state']
        shipping_details.zip_code = shipping_details_kwargs['zip_code']
        shipping_details.city = shipping_details_kwargs['city']
        shipping_details.street_name = shipping_details_kwargs['street_name']
        shipping_details.street_number = shipping_details_kwargs['street_number']
        shipping_details.save()
        
        status = 0
        message = 'Successfully updated your shipping information.'
        internal_message = message
    
    except Exception as error:
        
        status = 1
        message = 'Unable to update your shipping information, contact support@airplant.garden for assistance.'
        internal_message = traceback.format_exc()
        
    print('[Backend.views.ChangeShipping]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message)) 
    
    return HttpResponse(json.dumps({'status' : status, 'message' : message}))



@csrf_exempt
def FailedTransaction(request):

    ''' Accepts request from '/checkout', renders checkout.html template '''

    tools.PrintTitle('Backend.views.FailedTransaction')
    
    try:
        
        # debug:
        print('[Backend.views.FailedTransaction]: Got post request with [%s]' %request.POST)
        
        # unpack post request:
        braintree_webhook_request = request.POST

        # sample_notification = gateway.webhook_testing.sample_notification(
        #     "subscription_charged_unsuccessfully",
        #     "s_eb7c8f2eb104cc04ccdc7f24b0a78a2a"
        # )
        # braintree_webhook_request = sample_notification
        
        webhook_notification = gateway.webhook_notification.parse(braintree_webhook_request['bt_signature'], braintree_webhook_request['bt_payload'])
        
        # debug:
        print('[Backend.views.FailedTransaction]: Parsed webhook notifcation [%s]' %webhook_notification)
        
        # get subscription id:
        subscription_id = webhook_notification.subject['subscription']['id']
    
        # get the subscription object:
        subscription = Subscription.objects.get(braintree_subscription_id=subscription_id)
        
        # set active status to false:
        subscription.active_status = False
        subscription.save()
        
        status = 0
        message = 'Payment failed for subscription [%s], setting active status to false.' %subscription_id
        internal_message = message
    
    except:
        
        subscription_id = -1
        status = 1
        message = 'Payment failed for subscription [%s], unable to update database.' %subscription_id
        internal_message = message
        
    print('[Backend.views.FailedTransaction]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message)) 
    
    return HttpResponse(json.dumps({'status' : status, 'message' : message}))
    


@csrf_exempt
def PostponeSubscription(request):
    pass



@csrf_exempt
def ContinueSubscription(request):
    pass
    
    
    
@csrf_exempt
def Backend(request):
    
    user = User.objects.get(email='123123@dc.om')
    # example for getting street address street_name = user.profile.shipping_details.street_name
    
    # get subscription object:
    # for row in s ubcription_table:
    #if True:
    for x in range (1):
        subscription = Subscription.objects.get(user=user)

        # Step 2, check active status:
        print('[Backend.Backend] User [%s] has active set to [%s]' %(subscription, subscription.active_status))
        if subscription.active_status:
            pass
        else:
            ''' TODO reroute pipeline for inactive users '''
            continue
        
        
        # Step 3, check continue status:
        print('[Backend.Backend] User [%s] has continue_status set to [%s]' %(subscription, subscription.continue_status))
        if subscription.continue_status:
            pass
        else:
            ''' TODO reroute pipeline for users with non-continue '''
            continue
        
        
        # Step 4, check gift status:
        print('[Backend.Backend] User [%s] has gift_status set to [%s]' %(subscription, subscription.gift_status))
        if subscription.gift_status:
            print('[Backend.Backend] Using gift address')
        else:
            print('[Backend.Backend] Using regular address')
        
        
        # Step 4, charge user:
        try:
            print('[Backend.Backend] User [%s] has been successfully charged' %subscription)
        except:
            ''' TODO reroute pipeline for users with failed payments '''
            print('[Backend.Backend] User [%s] payment method failed' %subscription)
            continue
        
        
        # Step 5, update qued status:
        subscription.qued_status = True
        subscription.save()
        
        
        # Step 6, check qued status:
        print('[Backend.Backend] User [%s] has qued_status set to [%s]' %(subscription, subscription.qued_status))
        if subscription.qued_status:
            pass
        else:
            print('[Backend.Backend] User [%s] is not qued for fulfillment' %subscription)
            continue
        
        
        # Step 7, check fulfulled status:
        print('[Backend.Backend] User [%s] has fulfilled_status set to [%s]' %(subscription, subscription.fulfilled_status))
        if subscription.fulfilled_status:
            ''' TODO reroute pipeline for users that have been fulfilled '''
            print('[Backend.Backend] User [%s] has already been fulfilled' %subscription)
            continue
        else:
            pass
        
        
        # Step 8, fulfill order:
        print('[Backend.Backend] User [%s] fulfilling order' %subscription)
        print('[Backend.Backend] User [%s] printing order' %subscription)
        
        
        # Step 9, reset states:
        subscription.qued_status = False
        subscription.fulfilled_status = False
        print('[Backend.Backend] User [%s] states have been reset' %subscription)
        
        return HttpResponse('hello')