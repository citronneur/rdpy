'''
@author: sylvain
'''

class Layer(object):
    '''
    Network abstraction for protocol
    Try as possible to divide user protocol in layer
    default implementation is a transparent layer
    '''
    def __init__(self, presentation = None):
        '''
        Constructor
        '''
        #presentation layer higher layer in model
        self._presentation = presentation
        #transport layer under layer in model
        self._transport = None
        #auto set transport layer of own presentation layer
        if not self._presentation is None:
            self._presentation._transport = self
    
    def connect(self):
        '''
        call when transport layer is connected
        default is send connect event to presentation layer
        '''
        if not self._presentation is None:
            self._presentation.connect()
    
    def recv(self, data):
        '''
        signal that data is available for this layer
        call by transport layer
        default is to pass data to presentation layer
        '''
        if not self._presentation is None:
            self._presentation.recv(data)
      
    def send(self, data):
        '''
        classical use by presentation layer
        write data for this layer
        default pass data to transport layer
        '''
        if not self._transport is None:
            self._transport.send(data)
            
class LayerAutomata(Layer):
    '''
    layer with automata state
    we can set next recv function used
    '''
    def __init__(self, presentation = None):
        '''
        Constructor
        '''
        #call parent constructor
        Layer.__init__(self, presentation)
        
    def setNextState(self, callback = None):
        '''
        set recv function to next callback or
        '''
        if callback is None:
            callback = self.__class__.recv
        
        self.recv = callback

#twitsed layer concept
from twisted.internet import protocol
#first that handle stream     
from network import Stream, Type
from error import InvalidType

class RawLayer(protocol.Protocol, LayerAutomata):
    '''
    Inherit from protocol twisted class
    allow this protocol to wait until expected size of packet
    and use Layer automata to call next automata state
    '''
    def __init__(self, presentation = None):
        '''
        Constructor
        '''
        #call parent automata
        LayerAutomata.__init__(self, presentation)
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
            self.recv(expectedData)
            
    def connectionMade(self):
        '''
        inherit from twisted protocol
        '''
        #join two scheme
        self.connect()
            
    def expect(self, expectedLen, callback = None):
        '''
        new expected len
        '''
        self._expectedLen = expectedLen
        #default callback is recv from LayerAutomata
        self.setNextState(callback)
        
    def send(self, message):
        '''
        send stream on tcp layer
        '''
        if isinstance(message, Type):
            s = Stream()
            s.writeType(message)
            self.transport.write(s.getvalue())
        elif isinstance(message, Stream):
            self.transport.write(message.getvalue())
        else:
            raise InvalidType("expected Stream or Type")