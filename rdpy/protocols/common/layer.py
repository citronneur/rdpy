'''
Created on 5 sept. 2013

@author: sylvain
'''

class Layer(object):
    '''
    classdocs
    '''
    def __init__(self, presentation = None):
        '''
        Constructor
        '''
        self._presentation = presentation
        self._transport= None
        if not self._presentation is None:
            self._presentation._transport = self
    
    def connect(self):
        '''
        signal that the transport layer is OK
        '''
        if not self._presentation is None:
            self._presentation.connect()
    
    def read(self, data):
        '''
        signal that data is available for this layer
        '''
        if not self._presentation is None:
            self._presentation.read(data)
      
    def write(self, data):
        '''
        write using transport layer
        '''
        self.transport.write(data)