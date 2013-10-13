'''
Created on 5 sept. 2013

@author: sylvain
'''

from rdpy.protocol.common.protocolbuffer import ProtocolBuffer
from rdpy.protocol.common.layer import Layer
from rdpy.protocol.common.stream import Stream
class TPKT(ProtocolBuffer, Layer):
    '''
    classdocs
    '''
    def __init__(self, presentation = None):
        '''
        Constructor
        '''
        ProtocolBuffer.__init__(self)
        Layer.__init__(self, presentation)
        #last packet version read from header
        self._lastPacketVersion = 0
        #length may be coded on more than 1 bytes
        self._lastShortLength = 0
        
    def connectionMade(self):
        '''
        call when transport layer connection
        is made
        '''
        self.expect(2, self.readHeader)
        self.connect()
        
    def readHeader(self, data):
        #first read packet version
        self._lastPacketVersion = data.read_uint8()
        
        if self._lastPacketVersion == 3:
            data.read_uint8()
            self.expect(2, self.readExtendedHeader)
        else:
            self._lastShortLength = data.read_uint8()
            if self._lastShortLength & 0x80:
                self.expect(1, self.readExtendedFastPathHeader)
                return
            self.expect(self._lastShortLength - 2, self.readFastPath)
                
        
    def readExtendedHeader(self, data):
        self.expect(data.read_beuint16() - 4, self.readData)
    
    def readExtendedFastPathHeader(self, data):
        self._lastShortLength &= ~0x80
        self._lastShortLength = (self._lastShortLength << 8) + data.read_uint8()
        self.expect(self._lastShortLength - 3, self.readFastPath)
    
    def readFastPath(self, data):
        pass
    
    def readData(self, data):
        self._protocol.dataReceived(data)
        self.expect(2, self.readHeader)
        
    def write(self, data):
        s = Stream()
        s.write_uint8(3)
        s.write_uint8(0)
        s.write_beuint16(data.len + 4)
        s.write(data.getvalue())
        self.transport.write(s.getvalue())