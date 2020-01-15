from django.views.decorators.csrf import csrf_exempt
from django.urls import path
from . import views


urlpatterns = [
    path('backend/', views.Backend, name='backend'),   
    path('failed_braintree_transaction/', views.FailedTransaction, name='failed_braintree_transaction'), 
    path('profile/', views.Profile, name='profile'), 
    path('change_shipping/', views.ChangeShipping, name='change_shipping'), 
    path('change_payment/', views.ChangePayment, name='change_payment'),
    path('cancel_subscription/', views.CancelSubscription, name='cancel_subscription'), 
    path('reactivate_subscription/', views.ReactivateSubscription, name='reactivate_subscription'), 
    path('postpone_subscription/', views.PostponeSubscription, name='postpone_subscription'), 
    path('continue_subscription/', views.ContinueSubscription, name='continue_subscription'), 
]