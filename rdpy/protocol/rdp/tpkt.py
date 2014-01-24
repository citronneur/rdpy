'''
@author: sylvain
'''
from rdpy.network.layer import RawLayer
from rdpy.network.type import UInt8, UInt16Be, sizeof

class TPKT(RawLayer):
    '''
    TPKT layer in RDP protocol stack
    this layer only handle size of packet
    and determine if is a fast path packet
    '''
    #first byte of classic tpkt header
    TPKT_PACKET = UInt8(3)
    
    def __init__(self, presentation = None):
        '''
        Constructor
        '''
        RawLayer.__init__(self, presentation)
        #last packet version read from header
        self._lastPacketVersion = UInt8()
        #length may be coded on more than 1 bytes
        self._lastShortLength = UInt8()
        
    def connect(self):
        '''
        call when transport layer connection
        is made (inherit from RawLayer)
        '''
        #header is on two bytes
        self.expect(2, self.readHeader)
        #no connection automata on this layer
        if not self._presentation is None:
            self._presentation.connect()
        
    def readHeader(self, data):
        '''
        read header of TPKT packet
        '''
        #first read packet version
        data.readType(self._lastPacketVersion)
        #classic packet
        if self._lastPacketVersion == TPKT.TPKT_PACKET:
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
        '''
        header may be on 4 bytes
        '''
        #next state is read data
        size = UInt16Be()
        data.readType(size)
        self.expect(size.value - 4, self.readData)
    
    def readExtendedFastPathHeader(self, data):
        '''
        fast ath header may be on 1 byte more
        '''
        leftPart = UInt8()
        data.readType(leftPart)
        self._lastShortLength.value &= ~0x80
        self._lastShortLength.value = (self._lastShortLength.value << 8) + leftPart.value
        #next state is fast patn data
        self.expect(self._lastShortLength.value - 3, self.readFastPath)
    
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
        self._presentation.recv(data)
        self.expect(2, self.readHeader)
        
    def send(self, message):
        '''
        send encapsuled data
        '''
        RawLayer.send(self, (TPKT.TPKT_PACKET, UInt8(0), UInt16Be(sizeof(message) + 4), message))