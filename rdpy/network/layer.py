#
# Copyright (c) 2014 Sylvain Peyrefitte
#
# This file is part of rdpy.
#
# rdpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

"""
Join RDPY design with twisted design

RDPY use Layer Protocol design (like twisted)
"""

from rdpy.base.error import CallPureVirtualFuntion

class StreamListener(object):
    """
    Interface use to inform that we can handle receive stream
    """
    def recv(self, s):
        """
        Signal that data is available for this layer
        call by transport layer
        default is to pass data to presentation layer
        @param s: raw Stream receive from transport layer
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "recv", "StreamListener"))
    
class StreamSender(object):
    """
    Interface use to show stream sender capability 
    """
    def send(self, data):
        '''
        Send Stream on layer
        @param data: Type or tuple element handle by transport layer
        '''
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "send", "StreamSender"))
    
class Layer(object):
    """
    A simple double linked list with presentation and transport layer
    and a subset of event (connect and close)
    """
    def __init__(self, presentation = None):
        """
        @param presentation: presentation layer
        """
        #presentation layer higher layer in model
        self._presentation = presentation
        #transport layer under layer in model
        self._transport = None
        #auto set transport layer of own presentation layer
        if not self._presentation is None:
            self._presentation._transport = self
    
    def connect(self):
        """
        Call when transport layer is connected
        default is send connect event to presentation layer
        """
        if not self._presentation is None:
            self._presentation.connect()
    
    def close(self):
        """
        Close layer event
        default is sent to transport layer
        """
        if not self._transport is None:
            self._transport.close()
            
class LayerAutomata(Layer, StreamListener):
    """
    Layer with automata state
    we can set next recv function used for Stream packet
    """
    def __init__(self, presentation = None):
        """
        @param presentation: presentation Layer
        """
        #call parent constructor
        Layer.__init__(self, presentation)
        
    def setNextState(self, callback = None):
        """
        Set receive function to next callback or
        current self.recv function if it's None
        @param callback: a callable object that can 
        receive Layer, Stream parameters
        """
        if callback is None:
            callback = self.__class__.recv
        
        self.recv = callback

#twisted layer concept
from twisted.internet import protocol
#first that handle stream     
from type import Stream

class RawLayer(protocol.Protocol, LayerAutomata, StreamSender):
    """
    Inherit from protocol twisted class
    allow this protocol to wait until expected size of packet
    and use Layer automata to call next automata state
    """
    def __init__(self, presentation = None):
        """
        @param presentation: presentation layer in layer list
        """
        #call parent automata
        LayerAutomata.__init__(self, presentation)
        #data buffer received from twisted network layer
        self._buffer = ""
        #len of next packet pass to next state function
        self._expectedLen = 0
        
    def dataReceived(self, data):
        """
        Inherit from protocol class
        main event of received data
        @param data: string data receive from twisted
        """
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
        """
        inherit from twisted protocol
        """
        #join two scheme
        self.connect()
        
    def close(self):
        """
        Close raw layer
        """
        self.transport.loseConnection()
            
    def expect(self, expectedLen, callback = None):
        """
        Configure layer to change next state with callback only
        when expectLen bytes is received from transport layer
        @param expectedLen: in bytes length use to call next state
        @param callback: callback call when expected length bytes is received
        """
        self._expectedLen = expectedLen
        #default callback is recv from LayerAutomata
        self.setNextState(callback)
        
    def send(self, message):
        """
        Send Stream on TCP layer
        format message into raw stream understood by transport layer
        @param message: (tuple | Type)
        """
        s = Stream()
        s.writeType(message)
        self.transport.write(s.getvalue())