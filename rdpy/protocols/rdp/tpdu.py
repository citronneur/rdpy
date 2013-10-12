'''
Created on 5 sept. 2013

@author: sylvain
'''
from rdpy.protocols.common.layer import Layer
from rdpy.protocols.common.stream import Stream
class TPDU(Layer):
    '''
    classdocs
    '''
    X224_TPDU_CONNECTION_REQUEST =    0xE0
    X224_TPDU_CONNECTION_CONFIRM =    0xD0
    X224_TPDU_DISCONNECT_REQUEST =    0x80
    X224_TPDU_DATA =                  0xF0
    X224_TPDU_ERROR =                 0x70

    def __init__(self, presentation = None):
        '''
        Constructor
        '''
        Layer.__init__(self, presentation)
    
    def connect(self):
        self.writeMessage(TPDU.X224_TPDU_CONNECTION_REQUEST)
    
    def write(self, data):
        s = Stream()
        s.write_uint8(2)
        s.write_uint8(TPDU.X224_TPDU_DATA)
        s.write_uint8(0x80)
        s.write(data.getvalue())
        self._transport.write(data)
        
    def writeMessage(self, code):
        s = Stream()
        s.write_uint8(6);
        s.write_uint8(code);
        s.write_beuint16(0);
        s.write_beuint16(0);
        s.write_uint8(0);
        self.write(s)