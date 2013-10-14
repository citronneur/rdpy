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
        Exception.__init__(self, message)
        
