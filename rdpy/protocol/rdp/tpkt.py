'''
@author: sylvain
'''
from rdpy.protocol.common.protocolbuffer import ProtocolBuffer
from rdpy.protocol.common.layer import Layer
from rdpy.protocol.common.stream import Stream

class TPKT(ProtocolBuffer, Layer):
    '''
    TPKT layer in RDP protocol stack
    this layer only handle size of packet
    and determine if is a fast path packet
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
        is made (inherit from ProtocolBuffer)
        '''
        #header is on two bytes
        self.expect(2, self.readHeader)
        #no connection automata on this layer
        self.connect()
        
    def readHeader(self, data):
        '''
        read header of TPKT packet
        '''
        #first read packet version
        self._lastPacketVersion = data.read_uint8()
        #classic packet
        if self._lastPacketVersion == 3:
            data.read_uint8()
            #read end header
            self.expect(2, self.readExtendedHeader)
        else:
            #is fast path packet
            self._lastShortLength = data.read_uint8()
            if self._lastShortLength & 0x80:
                #size is 1 byte more
                self.expect(1, self.readExtendedFastPathHeader)
                return
            self.expect(self._lastShortLength - 2, self.readFastPath)
                
        
    def readExtendedHeader(self, data):
        '''
        header may be on 4 bytes
        '''
        #next state is read data
        self.expect(data.read_beuint16() - 4, self.readData)
    
    def readExtendedFastPathHeader(self, data):
        '''
        fast ath header may be on 1 byte more
        '''
        self._lastShortLength &= ~0x80
        self._lastShortLength = (self._lastShortLength << 8) + data.read_uint8()
        #next state is fast patn data
        self.expect(self._lastShortLength - 3, self.readFastPath)
    
    def readFastPath(self, data):
        '''
        fast path data
        '''
        pass
    
    def readData(self, data):
        '''
        read classic TPKT packet
        '''
        #next state is pass to 
        self.recv(data)
        self.expect(2, self.readHeader)
        
    def write(self, data):
        s = Stream()
        s.write_uint8(3)
        s.write_uint8(0)
        s.write_beuint16(data.len + 4)
        s.write(data.getvalue())
        self.transport.write(s.getvalue())