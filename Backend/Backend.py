import Backend.BackendFunctions as funcs
from Accounts.models import Subscription


def Backend(user):
    
    
    # get subscription object:
    for row in subcription_table:
        subscription = Subscription.objects.get(user=user)
        
        # Step 2, check active status:
        print('[Backend.Backend] User [%s] has active set to [%s]' %(subscription, subscription.active_status))
        if subcription.active_status:
            pass
        else:
            ''' TODO reroute pipeline for inactive users '''
            continue
        
        
        # Step 3, check continue status:
        print('[Backend.Backend] User [%s] has continue_status set to [%s]' %(subscription, subscription.continue_status))
        if continue_status:
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