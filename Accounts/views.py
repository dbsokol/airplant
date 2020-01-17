from .models import Profile, PersonalDetails, ShippingDetails, PaymentDetails, Coupon, Subscription, Customer, Discount
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.template import RequestContext
from datetime import datetime, timezone
from airplant.settings import gateway
from django.http import HttpResponse
import Tools.Tools as tools
from time import time
import traceback
import easypost
import hashlib
import json
import re



def LoadCheckout(request):

    ''' Accepts request from '/checkout', renders checkout.html template '''

    tools.PrintTitle('Accounts.views.LoadCheckout')
    
    return render(request, 'checkout.html')



def CheckEmail(request):
    
    ''' Accepts request from '/check_email', returns 1 if email is in use, 0 otherwise '''
    
    tools.PrintTitle('Accounts.views.CheckEmail')
    
    # get email from request:
    email = request.POST['email']

    # regex for valid email:
    regex = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,6})+$'

    # debug:
    print('[Accounts.views.CheckEmail]: Received email input from front-end [%s] ' %email)
    
    # check if email is invalid:
    if(not re.search(regex,email)):  
        
        status = 1
        internal_message = 'invalid email'
        message = 'Invalid email.'
        
        # debug:
        print('[Accounts.views.CheckEmail]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message)) 

        return HttpResponse(json.dumps({'message': message, 'status' : status}), content_type='application/json')
    
    # check if email is already in use:
    if User.objects.filter(email=email).exists():
        
        # check if user completed registration:
        if User.objects.get(email=email).profile.is_registered:
        
            # set message, status
            message = 'Email is already in use, <a style="text-decoration:underline" href="/login/"> log in instead.</a>'
            internal_message = 'email in use, user registered'
            status = 1
        
        # check if user never completed registration: 
        else:
            message = ''
            internal_message = 'email in use, user not registered'
            status = 0
        
    # check that email is not in use:
    else:
        message = ''
        internal_message = 'email available'
        status = 0

    # debug:
    print('[Accounts.views.CheckEmail]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message))
    
    return HttpResponse(json.dumps({'message': message, 'status' : status}), content_type='application/json')
    


def CheckPassword(request):
    
    ''' Accepts request from front end at '/check_password', returns password status '''
    
    tools.PrintTitle('Accounts.views.CheckPassword')
    
    # unpack request:
    password1 = request.POST['password1']
    password2 = request.POST['password2']
    
    # debug:
    print('[Accounts.views.CheckPassword]: Received passwords input from front-end 1:[%s], 2:[%s] ' %(password1, password2))
    
    # check if passwords match:
    if (password1 != password2):
        
        status = 1
        message = 'Passwords do not match'
        internal_message = message
        
        # debug:
        print('[Accounts.views.CheckPassword]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message))
        
        return HttpResponse(json.dumps({'message': message, 'status' : status}), content_type='application/json')
     
    # check length of password:
    if (len(password1) < 6):
        
        status = 1
        message = 'Passwords must be at least 6 characters'
        internal_message = message
        
        # debug:
        print('[Accounts.views.CheckPassword]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message))
        
        return HttpResponse(json.dumps({'message': message, 'status' : status}), content_type='application/json')
    
    # check if password contains only numbers or only letters:
    if (password1.isdigit() or password1.isalpha()):
        
        status = 1
        message = 'Passwords must contain at least 1 letter and 1 number'
        internal_message = message
        
        # debug:
        print('[Accounts.views.CheckPassword]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message))
        
        return HttpResponse(json.dumps({'message': message, 'status' : status}), content_type='application/json')
    
    status = 0
    message = 'Password okay'
    internal_message = message
    
    return HttpResponse(json.dumps({'message': message, 'status' : status}), content_type='application/json')



def GetDiscount(request):

    ''' Accepts requests to /get_discount, applies discount to given user '''
    
    tools.PrintTitle('Accounts.views.GetDiscount')
    
    try:
        
        # debug:
        print('[Accounts.views.GetDiscount]: Got post request with [%s]' %request.POST)
    
        # discount key word argments:
        discount_kwargs = {
            'email' :  request.POST['email'],
            'amount' : int(request.POST['amount']),
        }
    
        # create discount object:
        discount = Discount.objects.create(**discount_kwargs)
        discount.save()

        coupon_code = '5OFFAIRPLANT'

        status = 0
        internal_message = 'apllied discount of [%d] to user [%s]' %(discount_kwargs['amount'], discount_kwargs['email']) 
        message = 'Successfully applied discount!'

    # error handler:
    except Exception as e:
        
        coupon_code = '-1'
        
        status = 1
        internal_message = traceback.format_exc()
        message = 'Error, could not apply your discount.'

    print('[Accounts.views.GetDiscount]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message))

    return HttpResponse(json.dumps({'message': message, 'status' : status, 'coupon_code' : coupon_code}), content_type='application/json')
    
    

def CheckCoupon(request):
    
    ''' Checks coupon code from front end '''
    
    tools.PrintTitle('Accounts.views.CheckCoupon')
    
    try:
        
        # debug:
        print('[Accounts.views.CheckCoupon]: Got post request with [%s]' %request.POST)
    
        coupon_code = request.POST['coupon'].upper()
        
        # check if code is valid:
        if Coupon.objects.filter(coupon_code=coupon_code).exists():
            
            discount = Coupon.objects.get(coupon_code=coupon_code).discount
            
            status = 0
            internal_message = 'discount: %s' %discount
            message = 'Found coupon.'
            
        # if code is not valid:    
        else:
        
            discount = 0
        
            status = -1
            internal_message = 'coupon does not exist'
            message = 'Coupon does not exist.'

    # error handler:
    except Exception as e:
        
        discount = 0
        
        status = 1
        internal_message = traceback.format_exc()
        message = 'bad request (404)'

    print('[Accounts.views.CheckCoupon]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message))

    return HttpResponse(json.dumps({'message': message, 'status' : status, 'discount' : discount}))



def GetToken(request):
    
    ''' Sends braintree token to front end '''
    
    tools.PrintTitle('Accounts.views.GetToken')
    
    try:
        
        # debug:
        print('[Accounts.views.GetToken]: Got post request with [%s]' %request.POST)
        
        # get braintree token keyword argsuments:
        braintree_token_kwargs = {
            'id' : hashlib.md5((request.POST['email'] + str(datetime.now())).encode('utf-8')).hexdigest(),
            'email' : request.POST['email'],
            'first_name' : request.POST['first_name'],
            'last_name' : request.POST['last_name'],
            'phone' : request.POST['phone'],
        }
            
        # create braintree customer:    
        braintree_customer_result = gateway.customer.create(braintree_token_kwargs)
        braintree_client_token = gateway.client_token.generate({"customer_id" : braintree_token_kwargs['id'] })
        
        customer_id = braintree_token_kwargs['id']
        
        status = 0
        internal_message = 'built token with user email [%s]' %braintree_token_kwargs['email'] 
        message = 'built token'
    
        print('[Accounts.views.GetToken]: customer id [%s]' %braintree_token_kwargs['id'])
        print('[Accounts.views.GetToken]: Braintree customer [BraintreeResult:%s]' %braintree_customer_result.is_success)
        
    except Exception as e:
        
        print('[Accounts.views.GetToken]: Exception [%s]' %traceback.format_exc())
        
        customer_id = -1
        braintree_client_token = 0
        
        status = 1
        internal_message = 'error in token creation'
        message = 'could not build token'

    print('[Accounts.views.GetToken]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message))

    return HttpResponse(json.dumps({'message': message, 'status' : status, 'token' : braintree_client_token, 'customer_id' : customer_id}))



def RedeemDiscounts(request):
    
    ''' Accepts post request, returns discount object for Braintree '''
    
    # initialize variables:
    discounts = {}
        
    # apply discount if coupon code is provided:
    if Coupon.objects.filter(coupon_code=request.POST['coupon_code']).exists():
    
        dicounts =  {
            'add' : [{
                'inherited_from_id' : request.POST['coupon_code'],
                'amount' : 5
                }]
            }
            
        return discounts
        
    return discounts
    
    

def Register(request):

    ''' Accepts request from front end registers user '''

    tools.PrintTitle('Accounts.views.Register')

    # debug:
    # print('[Accounts.views.Register]: Received post request with [%s]' %request.POST)
    
    try:
        
        # get personal details key word arguments from front end:
        personal_details_kwargs = {
            'email' : request.POST['email'],
            'first_name' : request.POST['first_name'].capitalize(),
            'last_name' : request.POST['last_name'].capitalize(),
            'phone' : request.POST['phone'],
        }
        
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
        
        # get payment details key word arguments:
        payment_details_kwargs = {
            'email' : request.POST['email'],
            'braintree_payment_method_token' : None, # filled in after braintree payment method is created
            'braintree_payment_method_global_id' : None, # filled in after braintree payment method is created
            'payment_nonce' : request.POST['nonce'],
            'card_holder_name' : request.POST['card_name'],
            'card_type' : request.POST['card_type'],
            'last_four' : request.POST['last_four'],
            'expiration' : request.POST['expiration'],
            'start_date' : datetime.now(timezone.utc),
        }
        
        # get subscription object keywords:
        subscription_kwargs = {
            'email' : request.POST['email'],
            'braintree_subscription_id' : 's_0000_' + hashlib.md5((request.POST['email'] + str(time())).encode('utf-8')).hexdigest(),
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

        customer_kwargs = {
            'braintree_customer_id' : 'c_' + hashlib.md5((request.POST['email'] + str(time())).encode('utf-8')).hexdigest(),
            'braintree_customer_global_id' : None, # filled in after braintree customer is created
            'first_name' : request.POST['first_name'].capitalize(),
            'last_name' : request.POST['last_name'].capitalize(),
            'email' : request.POST['email'],
        }
        
        # get user key word arguments:
        user_kwargs = {
            'username' : request.POST['email'],
            'email' : request.POST['email'],
            'password' : request.POST['password1'],
        }
        
        # set braintree customer key word arguments:
        braintree_customer_kwargs = {
            'id' : customer_kwargs['braintree_customer_id'],
            'first_name' : request.POST['first_name'].capitalize(),
            'last_name' : request.POST['last_name'].capitalize(),
            'email' : request.POST['email'],
        }
        
        # set braintree payment_method key word arguments:
        braintree_payment_method_kwargs = {
            'customer_id' : customer_kwargs['braintree_customer_id'],
            'payment_method_nonce' : request.POST['nonce'],
        }
        
        # set braintree subscription keywords:
        braintree_subscription_kwargs = {
                'id' : subscription_kwargs['braintree_subscription_id'],
                'payment_method_token' : None, # filled in later 
                'plan_id' : 'Standard_Plan',
                'discounts' : RedeemDiscounts(request),
            }
            
        # create braintree customer:
        braintree_customer_result = gateway.customer.create(braintree_customer_kwargs)
        
        # debug:
        if not braintree_customer_result.is_success:
            print('[Accounts.views.Register]: Braintree error on customer create [%s]' %braintree_customer_result)
        
        # create braintree payment method:
        braintree_payment_method_result = gateway.payment_method.create(braintree_payment_method_kwargs)
        
        # debug:
        if not braintree_payment_method_result.is_success:
            print('[Accounts.views.Register]: Braintree error on payment method create [%s]' %braintree_payment_method_result)
        
        # create braintree subscription:
        braintree_subscription_kwargs['payment_method_token'] = braintree_payment_method_result.payment_method.token
        braintree_subscription_result = gateway.subscription.create(braintree_subscription_kwargs)
        
        if not braintree_subscription_result.is_success:
            print('[Accounts.views.Register]: Created braintree subscrption with [BraintreeResult:%s]' %braintree_subscription_result)
        
        # create personal details:
        personal_details = PersonalDetails.objects.create(**personal_details_kwargs)
        personal_details.save()
        
        # create shipping details:
        shipping_details = ShippingDetails.objects.create(**shipping_details_kwargs)
        shipping_details.save()
            
        # update payment method object:
        payment_details_kwargs['braintree_payment_method_token'] = braintree_payment_method_result.payment_method.token
        payment_details_kwargs['braintree_payment_method_global_id'] = braintree_payment_method_result.payment_method.global_id
        payment_details = PaymentDetails.objects.create(**payment_details_kwargs)
        payment_details.save()
            
        # create subscrption object in database:
        subscription_kwargs['next_billing_date'] = braintree_subscription_result.subscription.next_billing_date
        subscription_kwargs['billing_day_of_month'] = braintree_subscription_result.subscription.billing_day_of_month
        subscription = Subscription.objects.create(**subscription_kwargs)
        
        # create customer:
        customer_kwargs['braintree_customer_global_id'] = braintree_customer_result.customer.global_id
        customer = Customer.objects.create(**customer_kwargs)
        
        # create, save registered user:
        user = User.objects.create_user(**user_kwargs)
        user.save()
        
        # update profile fields:
        user.refresh_from_db()
        user.profile.personal_details = personal_details
        user.profile.shipping_details = shipping_details
        user.profile.payment_details = payment_details
        user.profile.subscription = subscription
        user.profile.customer = customer
        user.profile.is_registered = True
        user.save()
        
        # authenticate user and log them in:
        user = authenticate(username=user_kwargs['email'], password=user_kwargs['password'])
        login(request, user)
        
        status = 0
        internal_message = 'user successfully registered'
        message = 'Weclome!'

    # error handler:
    except Exception as e:
        
        status = 1
        internal_message = traceback.format_exc()
        message = 'Error in user registration.'

    print('[Accounts.views.Register]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message))    

    return HttpResponse(json.dumps({'message': message, 'status' : status}))
    
    
    
def Shipping(request):

    # ''' Accepts request from ship requet '''

    # tools.PrintTitle('Accounts.views.Ship')

    # # debug:
    # print('[Accounts.views.Ship]: Received post request with [%s]' %request.POST)
    
    # # create from address
    # easypost.api_key = 'EZTK6aa9c53aa3ba4cc6ae340255e42f29b63mZEbaBzBqSdFREqTWhNSw'
    # fromAddress = easypost.Address.create(
    #     company='TillandsiaGardens',
    #     street1='9415 Oakmore Rd.',
    #     street2='',
    #     city='Los Angeles',
    #     state='CA',
    #     zip='90035',
    #     phone='310-614-7904'
    # )
    # print('[Accounts.views.Ship]: Shipping From Address [%s]' %fromAddress)

    # # create to address  
    # toAddress = easypost.Address.create(
    #     name = personal_details.first_name + personal_details.last_name,
    #     street1 = shipping_details.address,
    #     street2 = shipping_details.address2,
    #     city = shipping_details.city,
    #     state = shipping_details.state,
    #     zip = shipping_details.zip'
    # )
    # print('[Accounts.views.Ship]: Shipping To Address [%s]' %toAddress)
    
    # parcel = easypost.Parcel.create(
    #     length=3,
    #     width=3,
    #     height=3,
    #     weight=2
    # )

    # # create parcel
    # shipment = easypost.Shipment.create(
    #     to_address=toAddress,
    #     from_address=fromAddress,
    #     parcel=parcel
    # )
  
    # print('[Accounts.views.Ship]: Shipping shipment [%s]' %shipment)

    # shipment.buy(rate=shipment.lowest_rate(carriers=['USPS'], services=['First']))

    # ## Print PNG link
    # print(shipment.postage_label.label_url)
    # ## Print Tracking Code
    # print(shipment.tracking_code)
    
    return render(request, 'index.html')

    
