from django.http import HttpResponse
from datetime import datetime
from time import time
import traceback
import pickle
import json




def PrintTitle(function_name):
    
    border = '   [' + '#' * (len(function_name) + 10) + ']\n'
    middle = '   [##| [' + function_name + '] |##]\n'  
    
    print('\n' + border + middle + border)
    


# Decorator tools:
def monitor_me(
    monitor = True,
    verbose_level = 2,
    save_output = False,
    ):
    
    ''' time_it decorator, used to time execution time of functions '''
    
    def decorator(function):
        
        def wrapper(*args, **kwargs):
        
            # intialize result object:
            result = {}
        
            # if monitor is set to false, do nothing:
            if not monitor:
                
                result['content'] = function(*args, **kwargs)
                result['status'] = -1
                result['message'] = "Set 'monitor' to True in Configuration to enable monitorting"
                
                return result['content']
        
            # start timer:
            function_start = time()
            
            # try to execute function:
            try:
                content = function(*args, **kwargs)
                status = 0
                message_body = 'Success'
            
            except:
                content = None
                status = 1
                message_body = 'Failure [%s]' %(traceback.format_exc())
                
            # terminate timer:
            function_end = time()

            current_time = datetime.now().strftime('%d/%b/%Y %H:%M:%S')

            # build message:
            message = "[%s] [%s] [Status: %s] [Message: %s] Function execution time [%7.2f s]" %(current_time, function.__name__, status, message_body, function_end-function_start)

            # print title:
            if verbose_level>=1:
                PrintTitle(function.__name__)

            # print post request:
            if verbose_level>=2:
                try:
                    post = args[0].POST
                except:
                    post = 'Unable to parse post request, is the first argument the request object?'
                print('[%s] [%s] Got post request with [%s]' %(current_time, function.__name__, post))
        
            # print execution time when verbose is true:
            if verbose_level>=1:
                print(message)
        
            # exception handler:
            if content is None:
                content = HttpResponse(json.dumps({'message': message, 'status' : status}), content_type='application/json')
        
            # pack result object:
            result['content'] = content
            result['status'] = status
            result['message'] = 'There was an error when processing your request, please contact support@airplant.garden for assistance.'
        
            # save output to .pkl file if save_output = True:
            if save_output:
                with open('/tmp/' + function.__name__ + '.pkl', 'wb') as handle:
                    pickle.dump(result, handle)
            
            return result['content']
        
        return wrapper
    
    return decorator



