from Accounts.models import Subscription, User, PersonalDetails, ShippingDetails, PaymentDetails
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Subscription_archive
import Backend.BackendFunctions as funcs
from datetime import datetime, timezone
from airplant.settings import gateway
from django.http import HttpResponse
import Tools.Tools as tools
import traceback
import hashlib
import json



@login_required(login_url='/login/')
def Profile(request):
    
    ''' Accepts request from '/profile', renders profile.html template '''

    tools.PrintTitle('Backend.views.Profile')
    
    try:
        
        # debug:
        print('[Backend.views.Profile]: Got post request with [%s]' %request.POST)
        
        user = request.user
        email = user.email
        personal_details = user.profile.personal_details
        shipping_details = user.profile.shipping_details
        payment_details = user.profile.payment_details
        subscription = user.profile.subscription
        context = {
            'personal_details' : {
                'first_name' : personal_details.first_name,
                'last_name' : personal_details.last_name,
                'email' : personal_details.email,
                },
            'payment_details' : { 
                'last_four' : payment_details.last_four,
                'card_type' : payment_details.card_type,
                'expiration' : payment_details.expiration,
                },
            'shipping_details' : {
                'first_name' : shipping_details.first_name,
                'last_name' : shipping_details.last_name,
                'country' : shipping_details.country,
                'state' : shipping_details.state,
                'zip_code' : shipping_details.zip_code,
                'city' : shipping_details.city,
                'street_name' : shipping_details.street_name,
                'street_number' : shipping_details.street_number,
                'address2' : shipping_details.address2,
                },
            'subscription' : {
                'active_status' : subscription.active_status if subscription else False,
                },
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
        
        # udpate subscription object:
        subscription.active_status = False
        subscription.end_date = datetime.now(timezone.utc)
        subscription.reason_for_canceling = str(reason_for_canceling)
        subscription.save()
        
        # get subscription id:
        braintree_subscription_id = subscription.braintree_subscription_id
    
        # cancel subscription:
        result = gateway.subscription.cancel(braintree_subscription_id)
        
        # subscription_archive keywords:
        subscription_archive_kwargs = {
            'user' : user.profile.personal_details.email,
            'braintree_subscription_id' : braintree_subscription_id,
            'subscription_name' : subscription.subscription_name,
            'shipping_details' : user.profile.shipping_details.address1 + ' ' + user.profile.shipping_details.address2,
            'start_date' : subscription.start_date,
            'end_date' : subscription.end_date, 
            'number_of_months' : (subscription.end_date.year - subscription.start_date.year) * 12 + subscription.end_date.month - subscription.start_date.month,
            'reason_for_canceling' : reason_for_canceling,
        }
        
        # archive subscription:
        Subscription_archive.objects.create(**subscription_archive_kwargs)
        
        # delete subscription object:
        subscription.delete()
        
        # debug:
        print('[Backend.views.CancelSubscription]: Canceled subscription with [%s]' %result)
        
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
        
        # get braintree payment method token
        payment_token = user.profile.payment_details.payment_token
        braintree_payment_method_result = gateway.payment_method.find(payment_token)
        print(braintree_payment_method_result)
        # get count of archived subscriptions:
        count = Subscription_archive.objects.filter(user=user.email).count()
        
        # create braintree_subscription_id:
        braintree_subscription_id = 's_' + hashlib.md5(user.email.encode('utf-8')).hexdigest() + '_' + str(count)
        
        # get subscription object keywords:
        subscription_kwargs = {
            'braintree_subscription_id' : braintree_subscription_id,
            'subscription_name' : 'Standard_Plan',
            'start_date' : datetime.now(timezone.utc),
            'active_status' : True,
            'continue_status' : True,
            'qued_status' : False,
            'fulfilled_status' : False,
            'gift_status' : False,
        }
        
        # create new subscription object:
        subscription = Subscription.objects.create(**subscription_kwargs)
        subscription.save()
        
        # register subscription to user:
        user.profile.subscription = subscription
        user.save()
        
        # create new braintree subscription:
        braintree_subscription_result = gateway.subscription.create({
            'id' : braintree_subscription_id,
            'payment_method_token' : user.profile.payment_details.payment_token,
            'plan_id' : 'Standard_Plan',
        })
        
        # debug:
        print('[Backend.views.ReactivateSubscription]: Created new subscription with id [%s]' %braintree_subscription_id)
        print('[Backend.views.ReactivateSubscription]: Reactivated subscription with [%s]' %braintree_subscription_result)
        
        status = 0
        message = 'You have successfully reactivated your subscription.'
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
        card_type = request.POST['card_type']
        expiration = request.POST['expiration']
        new_payment_method_token = request.POST['new_payment_method_token']
        
        # get payment details object:
        payment_details = PaymentDetails.objects.get(user=user)
        
        # update payment details object:
        payment_details.last_four = last_four
        payment_details.card_type = card_type
        payment_details.expiration = expiration
        payment_details.save()
        
        # get subscription obbject:
        subscription = Subscription.objects.get(user=user)
        
        # update subscription:
        braintree_subscription_id = subscription.braintree_subscription_id
        
        # update payment method in braintree subscription object:
        result = gateway.subscription.update(braintree_subscription_id, {
            'payment_method_token': new_payment_method_token,
        })
        
        # debug:
        print('[Backend.views.ChangePayment]: Changed braintree subscription payment method with [%s]' %result)
        
        status = 0
        message = 'Successfully updated your payment information.'
        internal_message = message
    
    except Exception as error:
        
        status = 1
        message = 'Unable to update your payment information, contact support@airplant.garden for assistance.'
        internal_message = traceback.format_exc()
        
    print('[Backend.views.ChangePayment]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message)) 
    
    return render(request, 'profile.html', context=context)



def ChangeShipping(request):
    
    ''' Accepts request /change_payment, changes the payment '''
    
    tools.PrintTitle('Backend.views.ChangeShipping')
    
    try:
        
        # debug:
        print('[Backend.views.ChangeShipping]: Got post request with [%s]' %request.POST)
        
        # get shipping details key word arguments from front end:
        shipping_details_kwargs = {
            'email' : request.POST['email'],
            'address1' : request.POST['address1'],
            'address2' : request.POST['address2'],
            'first_name' : request.POST['first_name'],
            'last_name' : request.POST['last_name'],
            'country' : request.POST['country'],
            'state' : request.POST['state'],
            'zip_code' : request.POST['zip_code'],
            'city' : request.POST['city'],
            'street_name' : request.POST['street_name'],
            'street_number' : request.POST['street_number'],     
        }
        
        # get payment details object:
        shipping_details = ShippingDetails.objects.get(user=user)
        
        # update payment details object:
        shipping_details.update(**shipping_details_kwargs)
        shipping_details.save()
        
        # # unpack post request:
        # address1 = request.POST['address1']
        # address2 = request.POST['address2']
        # country = request.POST['country']
        # state = request.POST['state']
        # zip_code = request.POST['zip_code']
        # city = request.POST['city']
        # street_name = request.POST['street_name']
        # street_number = request.POST['street_number']
        
        # # get shipping details object:
        # shipping_details = ShippingDetails.objects.get(user=user)
        
        # # update shipping details object:
        # shipping_details.address1 = address1
        # shipping_details.address2 = address2
        # shipping_details.country = country
        # shipping_details.state = state
        # shipping_details.zip_code = zip_code
        # shipping_details.city = city
        # shipping_details.street_name = street_name
        # shipping_details.street_number = street_number
        # shipping_details.save()
        
        # get subscription obbject:
        subscription = Subscription.objects.get(user=user)
        
        # update subscription:
        braintree_subscription_id = subscription.braintree_subscription_id
        
        # update payment method in braintree subscription object:
        result = gateway.subscription.update(braintree_subscription_id, {
            'payment_method_token': new_payment_method_token,
        })
        
        # debug:
        print('[Backend.views.ChangeShipping]: Changed braintree subscription payment method with [%s]' %result)
        
        status = 0
        message = 'Successfully updated your payment information.'
        internal_message = message
    
    except Exception as error:
        
        status = 1
        message = 'Unable to update your payment information, contact support@airplant.garden for assistance.'
        internal_message = traceback.format_exc()
        
    print('[Backend.views.ChangeShipping]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message)) 
    
    return render(request, 'profile.html', context=context)



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