from Accounts.forms import RegisterForm, PersonalDetailsForm, ShippingDetailsForm, PaymentDetailsForm
from .models import Profile, PersonalDetails, ShippingDetails, PaymentDetails, Coupon
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.template import RequestContext
from django.http import HttpResponse
from datetime import datetime
from airplant import settings
import Tools.Tools as tools
from time import time
import braintree
import hashlib
import json
import re



def LoadCheckout(request):

    ''' Accepts request from '/checkout', renders checkout.html template '''

    tools.PrintTitle('Accounts.views.LoadCheckout')
    
    form = RegisterForm()
    
    return render(request, 'checkout.html', {'form': form})



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
        if User.objects.get(email=email).profile.is_registered():
        
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



def GetPersonalDetails(request):

    ''' Retreives personal details from front end '''

    tools.PrintTitle('Accounts.views.GetPersonalDetails')

    try:
        
        # debug:
        print('[Accounts.views.GetPersonalDetails]: Got post request with [%s]' %request.POST)
        
        # unpack request:
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        phone = request.POST['phone']
        
        # if personal details already exists:
        if PersonalDetails.objects.filter(email=email).exists():

            # retreive existing personal details:
            personal_details = PersonalDetails.objects.get(email=email)
            
            # update user:
            personal_details.email = email
            personal_details.first_name = first_name
            personal_details.last_name = last_name
            personal_details.phone = phone
            personal_details.save()
            
            status = 0
            internal_message = 'personal details updated'
            message = 'Personal details updated.'
        
        # if personal details does not already exist:    
        else:        
            
            PersonalDetails.objects.create(email=email, first_name=first_name, last_name=last_name, phone=phone)
        
            status = 0
            internal_message = 'personal details captured'
            message = 'Thanks!'

    # invalid form:        
    except Exception as e:
        
        status = 1
        internal_message = e
        message = 'Unable to retreive personal details.'
        
    print('[Accounts.views.GetPersonalDetails]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message))    
    
    return HttpResponse(json.dumps({'message': message, 'status' : status}))



def GetShippingDetails(request):

    ''' Accepts shipping details from front end, updates database '''

    tools.PrintTitle('Accounts.views.GetShippingDetails')

    # debug:
    print('[Accounts.views.GetShippingDetails] Got request from front end with [%s]' %request.POST)

    try:
        email               = request.POST['email']
        address1            = request.POST['address1']
        address2            = request.POST['address2']
        address1            = request.POST['address1']
        address2            = request.POST['address2']
        first_name          = request.POST['first_name']      
        last_name           = request.POST['last_name']
        country             = request.POST['country']
        state               = request.POST['state']          
        zip_code            = request.POST['zip_code']   
        city                = request.POST['city']
        street_name         = request.POST['street_name']       
        street_number       = request.POST['street_number']

        # overwrite shipping detials for user if shipping details already exists:
        if ShippingDetails.objects.filter(personal_details=personal_details).exists():
            
            shipping_details = ShippingDetails.objects.get(email=email)
            shipping_details.personal_details    = PersonalDetails.objects.get(email=email),
            ###### END DEBUG ######
            
            shipping_details.address1            = address1,   
            shipping_details.address2            = address2,
            shipping_details.first_name          = first_name,        
            shipping_details.last_name           = last_name,  
            shipping_details.country             = country, 
            shipping_details.state               = state,             
            shipping_details.zip_code            = zip_code,   
            shipping_details.city                = city, 
            shipping_details.street_name         = street_name,       
            shipping_details.street_number       = street_number
            shipping_details.save()
            
            status = 0
            internal_message = 'valid shipping details form, updated existing shipping details object'
            message = 'valid address'
    
        # create new shipping details object:
        else:    
            ShippingDetails.objects.create(
                personal_details    = personal_details,  
                address1            = address1,   
                address2            = address2,
                first_name          = first_name,        
                last_name           = last_name,  
                country             = country, 
                state               = state,             
                zip_code            = zip_code,   
                city                = city, 
                street_name         = street_name,       
                street_number       = street_number
                )
        
            status = 0
            internal_message = 'valid shipping details form, created new shipping details object'
            message = 'valid address'
    
    # errors:   
    except Exception as e:
        status = 1
        internal_message = e
        message = 'invalid address'
        
    print('[Accounts.views.GetShippingDetails]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message))    

    return HttpResponse(json.dumps({'message': message, 'status' : status}))
    
        

def CheckCoupon(request):
    
    ''' Checks coupon code from front end '''
    
    tools.PrintTitle('Accounts.views.CheckCoupon')
    
    try:
        
        # debug:
        print('[Accounts.views.CheckCoupon]: Got post request with [%s]' %request.POST)
    
        email = request.POST['email']
        coupon_code = request.POST['coupon']
        
        # check if code is valid:
        if Coupon.objects.filter(coupon_code=coupon_code).exists():
            
            discount = Coupon.objects.get(coupon_code=coupon_code).discount
            
            status = 0
            internal_message = 'discount: %s' %discount
            message = 'Found coupon.'
            
        # if code is not valid:    
        else:
        
            discount = 0
        
            status = 0
            internal_message = 'coupon does not exist'
            message = 'Coupon does not exist.'

    # error handler:
    except Exception as e:
        
        discount = 0
        
        status = 1
        internal_message = e
        message = 'bad request (404)'

    print('[Accounts.views.CheckCoupon]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message))

    return HttpResponse(json.dumps({'message': message, 'status' : status, 'discount' : discount}))




def GetToken(request):
    
    ''' Sends braintree token to front end '''
    
    tools.PrintTitle('Accounts.views.GetToken')
    
    try:
        
        # debug:
        print('[Accounts.views.GetToken]: Got post request with [%s]' %request.POST)
        
        # get email:
        email = request.POST['email']
        
        # get personal_details:
        personal_details = PersonalDetails.objects.get(email=email)
        
        # configure braintree:
        braintree.Configuration.configure(
            settings.braintree_env,
            merchant_id=settings.BRAINTREE_MERCHANT_ID,
            public_key=settings.BRAINTREE_PUBLIC_KEY,
            private_key=settings.BRAINTREE_PRIVATE_KEY,
        )
        
        # create unique customer_id:
        customer_id = hashlib.md5(email.encode('utf-8'))
        customer_id = customer_id.hexdigest()
    
        # create braintree customer:    
        result = braintree.Customer.create({
            'id'        : customer_id,                  'first_name' : personal_details.first_name, 
            'last_name' : personal_details.last_name,   'phone'      : personal_details.phone, 
            'email'     : personal_details.email
        })
        braintree_client_token = braintree.ClientToken.generate({"customer_id" : customer_id })
        
        # subscripotion
        # result2 = braintree.Subscription.create({
        #     'payment_method_token' : braintree_client_token,
        #     'plan_id' : 'Standard_Plan'
        # })
        
        status = 0
        internal_message = 'built token with user email [%s]' %email 
        message = 'built token'
    
        print('[Accounts.views.GetToken]: customer id [%s]' %customer_id)
        print('[Accounts.views.GetToken]: Braintree customer [%s]' %result)
        # print('[Accounts.views.GetToken]: Braintree subscription [%s]' %result2)

    except Exception as e:
        
        print('[Accounts.views.GetToken]: Exception [%s]' %e)
        
        braintree_client_token = 0
        
        status = 1
        internal_message = 'error in token creation'
        message = 'could not build token'

    print('[Accounts.views.GetToken]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message))

    return HttpResponse(json.dumps({'message': message, 'status' : status, 'token' : braintree_client_token}))



def GetPayment(request):
    
    ''' Executes payment '''
    
    tools.PrintTitle('Accounts.views.GetPayment')
    
    # get token, email:
    token = request.POST['token']
    email = request.POST['email']
    
    # get personal details:
    personal_details = PersonalDetails.objects.get(email=email)
    first_name = personal_details.first_name
    last_name = personal_details.last_name
    
    # create kwargs dictionary:
    customer_kwargs = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
    }
    
    # create customer:
    customer_create = braintree.Customer.create(customer_kwargs)
    customer_id = customer_create.customer.id
    result = braintree.Transaction.sale({
        "amount": "10.00",
        "payment_method_nonce": nonce_from_the_client,
        "options": {
            "submit_for_settlement": True
        }
    })
    print(result)
    
    status = 0
    internal_message = 'billed client'
    message = 'payment successful'

    print('[Accounts.views.GetPayment]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message))

    return HttpResponse(json.dumps({'message': message, 'status' : status}))



def SubmitNonce(request):
    
    tools.PrintTitle('Accounts.views.SubmitNonce')
    
    # debug:
    print('[Accounts.views.SubmitNonce]: Received post request with [%s]' %request.POST)
    
    try:
        email = request.POST['email']
        nonce = request.POST['nonce']
        card_type = request.POST['card_type']
        last_four = request.POST['last_four']
        discount = request.POST['discount']

        # get user by email:
        personal_details = PersonalDetails.objects.get(email=email)
        
        # create new payment details object:
        PaymentDetails.objects.create(
            personal_details    = personal_details, 
            payment_token       = nonce,
            card_type           = card_type,
            last_four           = last_four,
            start_date          = datetime.now()
            )
            
        status = 0
        internal_message = 'valid payment details, created new payment details object'
        message = 'valid payment details'
            
        # subscripotion
        result2 = braintree.Subscription.create({
            'payment_method_token' : nonce,
            'plan_id' : 'Standard_Plan',
            'discount' : discount,
        })
    
    # errors:   
    except Exception as e:
        status = 1
        internal_message = e
        message = 'invalid payment details'
        
    print('[Accounts.views.SubmitNonce]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message))    

    return HttpResponse(json.dumps({'message': message, 'status' : status}))
    


def Register(request):

    ''' Accepts request from front end registers user '''

    tools.PrintTitle('Accounts.views.Register')

    # debug:
    print('[Accounts.views.Register]: Received post request with [%s]' %request.POST)
    
    try:
        
        # unpack request
        email = request.POST['email']
        password = request.POST['password1']
        
        # create registered user:
        user = User.objects.create(
            username    = email,
            password    = password
            )
        user.save()
        
        # update profile fields:
        user.refresh_from_db()
        user.profile.personal_details = PersonalDetails.objects.get(email=email)
        user.profile.shipping_details = ShippingDetails.objects.get(email=email)
        user.profile.payment_details = PaymentDetails.objects.get(email=email)
        
        user = authenticate(username=user.username, password=password)
        login(request, user)
        
        # user = form.save()
        # user.refresh_from_db()  # load the profile instance created by the signal
        # user.username = form.cleaned_data.get('email')
        # user.profile.phone = form.cleaned_data.get('phone')
        # user.first_name = form.cleaned_data.get('first_name')
        # user.last_name = form.cleaned_data.get('last_name')
        # user.save()
        # raw_password = form.cleaned_data.get('password1')
        # user = authenticate(username=user.username, password=raw_password)
        
        status = 0
        internal_message = 'user registered'
        message = 'Weclome!'

    except Exception as e:
        
        status = 1
        internal_message = e
        message = 'Error in user registration'

    print('[Accounts.views.Register]: [Status: %s] [Internal Message: %s] [Message: %s]' %(status, internal_message, message))    

    return HttpResponse(json.dumps({'message': message, 'status' : status}))
    

    
@login_required(login_url='/login/')
def Profile(request):
    
    return render(request, 'profile.html')