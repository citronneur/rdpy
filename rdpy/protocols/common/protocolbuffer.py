'''
Created on 17 aout 2013

@author: sylvain
'''
from twisted.internet import protocol
from stream import Stream

class ProtocolBuffer(protocol.Protocol):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        #data buffer received from twisted network layer
        self._buffer = ""
        
        #len of next packet pass to next state function
        self._expectedLen = 0
        
    def dataReceived(self, data):
        '''
        inherit from protocol class
        main event of received data
        '''
        self._buffer += data
        while len(self._buffer) >= self._expectedLen:
            expectedData = Stream(self._buffer[0:self._expectedLen])
            self._buffer = self._buffer[self._expectedLen:]
            self.recv(expectedData)
            
    def expect(self, expectedLen, callback = None):
        '''
        newt expected len
        '''
        self._expectedLen = expectedLen
        
        if callback is None:
            callback = self.__class__.recv
        
        self.recv = callback
        
    def recv(self, data):
        '''
        call when expected data is receive
        '''
        pass