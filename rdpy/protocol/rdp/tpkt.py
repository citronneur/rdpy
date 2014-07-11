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
from rdpy.network.layer import RawLayer, LayerMode
from rdpy.network.type import UInt8, UInt16Be, sizeof
from rdpy.network.error import CallPureVirtualFuntion

class FastPathListener(object):
    """
    Fast path packet listener
    Usually PDU layer
    """
    def recvFastPath(self, fastPathData):
        """
        Call when fast path packet is received
        @param fastPathData: Stream
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "recv", "StreamListener"))

class TPKT(RawLayer):
    """
    TPKT layer in RDP protocol stack
    This layer only handle size of packet and determine if is a fast path packet
    """
    #first byte of classic tpkt header
    TPKT_PACKET = 3
    
    def __init__(self, presentation, fastPathListener):
        """
        @param presentation: presentation layer, in RDP case is TPDU layer
        """
        RawLayer.__init__(self, LayerMode.NONE, presentation)
        #last packet version read from header
        self._lastPacketVersion = UInt8()
        #length may be coded on more than 1 bytes
        self._lastShortLength = UInt8()
        #fast path listener
        self._fastPathListener = fastPathListener
        
    def connect(self):
        """
        Call when transport layer connection
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
        data.readType(self._lastPacketVersion)
        #classic packet
        if self._lastPacketVersion.value == TPKT.TPKT_PACKET:
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
        RawLayer.send(self, (UInt8(TPKT.TPKT_PACKET), UInt8(0), UInt16Be(sizeof(message) + 4), message))