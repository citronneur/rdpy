'''
@author: sylvain
'''

class InvalidExpectedDataException(Exception):
    '''
    raise when expected data on network is invalid
    '''
    def __init__(self, message):
        '''
        constructor with message
        '''
        self._message = message
        
    def __str__(self):
        '''
        return string representation of exception
        '''
        return "%s"%self._message
        
