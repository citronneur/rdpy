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
Transport packet layer implementation

Use to build correct size packet and handle slow path and fast path mode
"""
from rdpy.network.layer import RawLayer
from rdpy.network.type import UInt8, UInt16Be, sizeof
from rdpy.base.error import CallPureVirtualFuntion

class Action(object):
    """
    @see: http://msdn.microsoft.com/en-us/library/cc240621.aspx
    @see: http://msdn.microsoft.com/en-us/library/cc240589.aspx
    """
    FASTPATH_ACTION_FASTPATH = 0x0
    FASTPATH_ACTION_X224 = 0x3

class IFastPathListener(object):
    """
    @summary:  Fast path packet listener
                Usually X224 layer
    """
    def recvFastPath(self, fastPathS):
        """
        @summary: Call when fast path packet is received
        @param fastPathS: Stream
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "recvFastPath", "recvFastPath"))
    
    def setFastPathSender(self, fastPathSender):
        """
        @summary: Call to set a fast path sender to listener
        @param fastPathSender: IFastPathSender
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "setFastPathSender", "recvFastPath"))

class IFastPathSender(object):
    """
    @summary: Fast path send capability
    """
    def sendFastPath(self, fastPathS):
        """
        @summary: Send fastPathS Type as fast path packet
        @param fastPathS: type transform to stream and send as fastpath
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "sendFastPath", "IFastPathSender"))

class TPKT(RawLayer, IFastPathSender):
    """
    @summary:  TPKT layer in RDP protocol stack
                represent the Raw Layer in stack (first layer)
                This layer only handle size of packet and determine if is a fast path packet
    """
    def __init__(self, presentation, fastPathListener = None):
        """
        @param presentation: presentation layer, in RDP case is x224 layer
        @param fastPathListener: IFastPathListener
        """
        RawLayer.__init__(self, presentation)
        #length may be coded on more than 1 bytes
        self._lastShortLength = UInt8()
        #fast path listener
        self._fastPathListener = fastPathListener
        
        if not fastPathListener is None:
            #set me as fast path sender
            fastPathListener.setFastPathSender(self)
        
    def connect(self):
        """
        @summary:  Call when transport layer connection
                    is made (inherit from RawLayer)
        """
        #header is on two bytes
        self.expect(2, self.readHeader)
        #no connection automata on this layer
        if not self._presentation is None:
            self._presentation.connect()
        
    def readHeader(self, data):
        """
        Read header of TPKT packet
        @param data: Stream received from twisted layer
        """
        #first read packet version
        version = UInt8()
        data.readType(version)
        #classic packet
        if version.value == Action.FASTPATH_ACTION_X224:
            #padding
            data.readType(UInt8())
            #read end header
            self.expect(2, self.readExtendedHeader)
        else:
            #is fast path packet
            data.readType(self._lastShortLength)
            if self._lastShortLength.value & 0x80:
                #size is 1 byte more
                self.expect(1, self.readExtendedFastPathHeader)
                return
            self.expect(self._lastShortLength.value - 2, self.readFastPath)
                
        
    def readExtendedHeader(self, data):
        """
        Header may be on 4 bytes
        @param data: Stream from twisted layer
        """
        #next state is read data
        size = UInt16Be()
        data.readType(size)
        self.expect(size.value - 4, self.readData)
    
    def readExtendedFastPathHeader(self, data):
        """
        Fast path header may be on 1 byte more
        @param data: Stream from twisted layer
        """
        leftPart = UInt8()
        data.readType(leftPart)
        self._lastShortLength.value &= ~0x80
        packetSize = (self._lastShortLength.value << 8) + leftPart.value
        #next state is fast patn data
        self.expect(packetSize - 3, self.readFastPath)
    
    def readFastPath(self, data):
        """
        Fast path data
        @param data: Stream from twisted layer
        """
        self._fastPathListener.recvFastPath(data)
        self.expect(2, self.readHeader)
    
    def readData(self, data):
        """
        Read classic TPKT packet, last state in tpkt automata
        @param data: Stream with correct size
        """
        #next state is pass to 
        self._presentation.recv(data)
        self.expect(2, self.readHeader)
        
    def send(self, message):
        """
        Send encompassed data
        @param message: network.Type message to send
        """
        RawLayer.send(self, (UInt8(Action.FASTPATH_ACTION_X224), UInt8(0), UInt16Be(sizeof(message) + 4), message))
        
    def sendFastPath(self, fastPathS):
        """
        @param fastPathS: type transform to stream and send as fastpath
        """
        RawLayer.send(self, (UInt8(Action.FASTPATH_ACTION_FASTPATH), UInt16Be((sizeof(fastPathS) + 3) | 0x8000), fastPathS))