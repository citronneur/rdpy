'''
@author: sylvain
'''
from rdpy.protocol.common.layer import LayerAutomata
from rdpy.protocol.common.stream import Stream
from rdpy.protocol.common.error import InvalidExpectedDataException, NegotiationFailure

class TPDU(LayerAutomata):
    '''
    classdocs
    '''
    X224_TPDU_CONNECTION_REQUEST =    0xE0
    X224_TPDU_CONNECTION_CONFIRM =    0xD0
    X224_TPDU_DISCONNECT_REQUEST =    0x80
    X224_TPDU_DATA =                  0xF0
    X224_TPDU_ERROR =                 0x70
    
    #negotiation header
    TYPE_RDP_NEG_REQ =                  0x01
    TYPE_RDP_NEG_RSP =                  0x02
    TYPE_RDP_NEG_FAILURE =              0x03
    #rdp negotiation protocol
    PROTOCOL_RDP =                      0x00000000
    PROTOCOL_SSL =                      0x00000001
    PROTOCOL_HYBRID =                   0x00000002
    PROTOCOL_HYBRID_EX =                0x00000008

    def __init__(self, presentation = None):
        '''
        Constructor
        '''
        LayerAutomata.__init__(self, presentation)
        
        #default protocol is SSl because is the only supported
        #in this version of RDPY
        self._protocol = TPDU.PROTOCOL_SSL
    
    def connect(self):
        '''
        connection request
        for client send a connection request packet
        '''
        self.sendConnectionRequest()

    def readHeader(self, data):
        '''
        read a typical TPDU header (len and code)
        '''            
        return data.read_uint8(), data.read_uint8()
    
    def recvConnectionConfirm(self, data):
        '''
        recv connection confirm message
        '''
        (len, code) = self.readHeader(data)
        if code != TPDU.X224_TPDU_CONNECTION_CONFIRM:
            raise InvalidExpectedDataException("invalid TPDU header code X224_TPDU_CONNECTION_CONFIRM != %d"%code)
        data.read_leuint32()
        data.read_uint8()
        #check presence of negotiation response
        if data.dataLen() == 8:
            self.readNeg(data)
        
    def sendConnectionRequest(self):
        '''
        write connection request message
        '''
        s = Stream()
        self.writeNegReq(s)
        self.sendMessage(TPDU.X224_TPDU_CONNECTION_REQUEST, s)
        self.setNextState(self.recvConnectionConfirm)
        
    def send(self, data):
        '''
        write message packet for TPDU layer
        add TPDU header
        '''
        s = Stream()
        s.write_uint8(2)
        s.write_uint8(TPDU.X224_TPDU_DATA)
        s.write_uint8(0x80)
        s.write(data.getvalue())
        self._transport.send(data)
        
    def sendMessage(self, code, data = Stream()):
        '''
        special write function
        that packet TPDU message
        '''
        s = Stream()
        s.write_uint8(6 + data.len)
        s.write_uint8(code)
        s.write_beuint16(0)
        s.write_beuint16(0)
        s.write_uint8(0)
        if data.len > 0:
            s.write(data.getvalue())
        self._transport.send(s)
        
    def writeNegReq(self, s):
        '''
        write negociation request structure
        '''
        s.write_uint8(TPDU.TYPE_RDP_NEG_REQ)
        #flags
        s.write_uint8(0)
        #write fixed packet size
        s.write_leuint16(0x0008)
        #write protocol
        s.write_leuint32(self._protocol)
        
    def readNeg(self, data):
        '''
        read neagotiation response
        '''
        code = data.read_uint8()
        
        if code == TPDU.TYPE_RDP_NEG_FAILURE:
            self.readNegFailure(data)
        elif code == TPDU.TYPE_RDP_NEG_RSP:
            self.readNegResp(data)
        else:
            raise InvalidExpectedDataException("bad protocol negotiation response code")
        #_transport is TPKT and transport is TCP layer of twisted
        self._transport.transport.startTLS(ClientTLSContext())
    
    def readNegFailure(self, data):
        '''
        read negotiation failure packet
        '''
        pass
    
    def readNegResp(self, data):
        '''
        read negotiation response packet
        '''
        flag = data.read_uint8()
        len = data.read_leuint16()
        
        if len != 0x0008:
            raise InvalidExpectedDataException("invalid size of negotiation response")
        
        protocol = data.read_leuint32()
        if protocol != self._protocol:
            raise NegotiationFailure("protocol negotiation failure")
        

#open ssl needed
from twisted.internet import ssl
from OpenSSL import SSL

class ClientTLSContext(ssl.ClientContextFactory):
    '''
    client context factory for open ssl
    '''
    isClient = 1
    def getContext(self):
        context = SSL.Context(SSL.TLSv1_METHOD)
        context.set_options(SSL.OP_DONT_INSERT_EMPTY_FRAGMENTS)
        context.set_options(SSL.OP_TLS_BLOCK_PADDING_BUG)
        return context