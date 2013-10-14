'''
Created on 5 sept. 2013

@author: sylvain
'''
from rdpy.protocol.common.layer import Layer
from rdpy.protocol.common.stream import Stream
from rdpy.protocol.common.error import InvalidExpectedDataException
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
        
    def recv(self, data):
        '''
        main receive function
        layer complexity doesn't need automata
        '''
        #unused length
        len = data.read_uint8()
        code = data.read_uint8()
        
        if code == TPDU.X224_TPDU_DATA:
            data.read_uint8()
            self._presentation.recv(data)
        else:
            #padding
            data.read_leuint32()
            if code == TPDU.X224_TPDU_CONNECTION_CONFIRM:
                self._presentation.connect()
            elif code == TPDU.X224_TPDU_CONNECTION_REQUEST:
                self.writeMessage(TPDU.X224_TPDU_CONNECTION_CONFIRM)
                self._presentation.connect()
            else:
                raise InvalidExpectedDataException("invalid TPDU header code %d"%code) 
    
    def write(self, data):
        '''
        write message packet for TPDU layer
        add TPDU header
        '''
        s = Stream()
        s.write_uint8(2)
        s.write_uint8(TPDU.X224_TPDU_DATA)
        s.write_uint8(0x80)
        s.write(data.getvalue())
        self._transport.write(data)
        
    def writeMessage(self, code):
        '''
        special write function
        that packet TPDU message
        '''
        s = Stream()
        s.write_uint8(6)
        s.write_uint8(code)
        s.write_beuint16(0)
        s.write_beuint16(0)
        s.write_uint8(0)
        self.write(s)