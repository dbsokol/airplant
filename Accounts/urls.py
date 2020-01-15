from django.urls import path
from . import views


urlpatterns = [
    path('checkout/', views.LoadCheckout, name='checkout'),
    path('check_email/', views.CheckEmail, name='check_email'),
    path('check_password/', views.CheckPassword, name='check_password'),
    path('get_discount/', views.GetDiscount, name='get_discount'),
    path('check_coupon/', views.CheckCoupon, name='check_coupon'),
    path('get_token/', views.GetToken, name='get_token'),
    path('register/', views.Register, name='register'),
    path('ship/', views.Shipping, name='ship'),
]