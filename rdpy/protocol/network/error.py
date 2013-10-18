'''
@author: sylvain
'''

class InvalidValue(Exception):
    '''
    raise when invalid value type occured
    '''
    def __init__(self, message = ""):
        '''
        constructor with message
        '''
        Exception.__init__(self, message)

class InvalidExpectedDataException(Exception):
    '''
    raise when expected data on network is invalid
    '''
    def __init__(self, message = ""):
        '''
        constructor with message
        '''
        Exception.__init__(self, message)
        
class NegotiationFailure(Exception):
    '''
    raise when negotiation failure in different protocols
    '''
    def __init__(self, message = ""):
        '''
        constructor with message
        '''
        Exception.__init__(self, message)
        
class InvalidType(Exception):
    '''
    raise when invalid value type occured
    '''
    def __init__(self, message = ""):
        '''
        constructor with message
        '''
        Exception.__init__(self, message)
        
