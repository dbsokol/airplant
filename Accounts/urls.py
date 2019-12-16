from django.urls import path
from . import views


urlpatterns = [
    path('checkout/', views.LoadCheckout, name='checkout'),
    #path('personal_details/', views.GetPersonalDetails, name='personal_details'),
    #path('shipping_details/', views.GetShippingDetails, name='shipping_details'),
    path('check_email/', views.CheckEmail, name='check_email'),
    path('check_password/', views.CheckPassword, name='check_password'),
    path('check_coupon/', views.CheckCoupon, name='check_coupon'),
    path('get_token/', views.GetToken, name='get_token'),
    #path('submit_nonce/', views.SubmitNonce, name='submit_nonce'),
    path('register/', views.Register, name='register'),
    path('ship/', views.Shipping, name='ship'),
]