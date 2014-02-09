'''
@author: sylvain
'''

class LayerMode(object):
    NONE = 0
    SERVER = 1
    CLIENT = 2

class Layer(object):
    '''
    Network abstraction for protocol
    Try as possible to divide user protocol in layer
    default implementation is a transparent layer
    '''
    def __init__(self, mode = LayerMode.NONE, presentation = None):
        '''
        Constructor
        @param presentation: Layer which handled connect and recv messages
        '''
        #presentation layer higher layer in model
        self._presentation = presentation
        #transport layer under layer in model
        self._transport = None
        #register layer mode
        self._mode = mode
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
    
    def recv(self, s):
        '''
        signal that data is available for this layer
        call by transport layer
        default is to pass data to presentation layer
        @param s: raw Stream receive from transport layer
        '''
        if not self._presentation is None:
            self._presentation.recv(s)
      
    def send(self, data):
        '''
        classical use by presentation layer
        write data for this layer
        default pass data to transport layer
        @param data: Type or tuple element handle by transport layer
        '''
        if not self._transport is None:
            self._transport.send(data)
    
    def close(self):
        '''
        close layer and send close signal 
        to transport layer
        '''
        if not self._transport is None:
            self._transport.close()
            
class LayerAutomata(Layer):
    '''
    layer with automata state
    we can set next recv function used
    '''
    def __init__(self, mode, presentation = None):
        '''
        Constructor
        @param presentation: presentation Layer
        '''
        #call parent constructor
        Layer.__init__(self, mode, presentation)
        
    def setNextState(self, callback = None):
        '''
        set recv function to next callback or
        current self.recv function if it's None
        @param callback: a callable object that can 
        receive Layer, Stream parameters
        '''
        if callback is None:
            callback = self.__class__.recv
        
        self.recv = callback

#twitsed layer concept
from twisted.internet import protocol
#first that handle stream     
from type import Stream

class RawLayer(protocol.Protocol, LayerAutomata):
    '''
    Inherit from protocol twisted class
    allow this protocol to wait until expected size of packet
    and use Layer automata to call next automata state
    '''
    def __init__(self, mode, presentation = None):
        '''
        Constructor
        '''
        #call parent automata
        LayerAutomata.__init__(self, mode, presentation)
        #data buffer received from twisted network layer
        self._buffer = ""
        #len of next packet pass to next state function
        self._expectedLen = 0
        
    def dataReceived(self, data):
        '''
        inherit from protocol class
        main event of received data
        @param data: string data receive from twisted
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
        configure layer to change next state with callback only
        when expectLen bytes is received from transport layer
        @param expectedLen: in bytes len use to call nextstate
        @param callback: callback call when expectedlen bytes is received
        '''
        self._expectedLen = expectedLen
        #default callback is recv from LayerAutomata
        self.setNextState(callback)
        
    def send(self, message):
        '''
        send stream on tcp layer
        format message into raw stream understood by transport layer
        @param message: (tuple | Type)
        '''
        s = Stream()
        s.writeType(message)
        self.transport.write(s.getvalue())