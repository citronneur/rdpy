'''
@author: sylvain
'''
from twisted.internet import protocol
from stream import Stream

class ProtocolBuffer(protocol.Protocol):
    '''
    Inherit from protocol twisted class
    allow this protocol to wait until expected size of packet
    throw expect function and set a callback or by default
    call recv function (may be override)
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
        #add in buffer
        self._buffer += data
        #while buffer have expected size call local callback
        while len(self._buffer) >= self._expectedLen:
            #expected data is first expected bytes
            expectedData = Stream(self._buffer[0:self._expectedLen])
            #rest is for next event of automata
            self._buffer = self._buffer[self._expectedLen:]
            #call recv function
            self.recvExpectedData(expectedData)
            
    def expect(self, expectedLen, callback = None):
        '''
        new expected len
        '''
        self._expectedLen = expectedLen
        
        #default callback is recvExpectedData
        if callback is None:
            callback = self.__class__.recvExpectedData
        
        self.recvExpectedData = callback
        
    def recvExpectedData(self, data):
        '''
        call when expected data is receive
        '''
        pass