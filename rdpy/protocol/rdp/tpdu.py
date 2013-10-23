'''
@author: sylvain
'''
from rdpy.protocol.network.layer import LayerAutomata
from rdpy.protocol.network.type import UInt8, UInt16Le, UInt16Be, UInt32Le, CompositeType, sizeof
from rdpy.protocol.network.error import InvalidExpectedDataException, NegotiationFailure
from rdpy.utils.const import ConstAttributes

@ConstAttributes
class MessageType(object):
    '''
    message type
    '''
    X224_TPDU_CONNECTION_REQUEST = UInt8(0xE0)
    X224_TPDU_CONNECTION_CONFIRM = UInt8(0xD0)
    X224_TPDU_DISCONNECT_REQUEST = UInt8(0x80)
    X224_TPDU_DATA = UInt8(0xF0)
    X224_TPDU_ERROR = UInt8(0x70)

@ConstAttributes
class NegociationType(object):
    '''
    negotiation header
    '''
    TYPE_RDP_NEG_REQ = UInt8(0x01)
    TYPE_RDP_NEG_RSP = UInt8(0x02)
    TYPE_RDP_NEG_FAILURE = UInt8(0x03)

@ConstAttributes
class Protocols(object):
    '''
    protocols available for TPDU layer
    '''
    PROTOCOL_RDP = UInt32Le(0x00000000)
    PROTOCOL_SSL = UInt32Le(0x00000001)
    PROTOCOL_HYBRID = UInt32Le(0x00000002)
    PROTOCOL_HYBRID_EX = UInt32Le(0x00000008)
    
class TPDUConnectHeader(CompositeType):
    '''
    header of TPDU connection messages 
    '''
    def __init__(self, code = MessageType.X224_TPDU_CONNECTION_REQUEST, messageSize = 0):
        CompositeType.__init__(self)
        self.len = UInt8(messageSize + 6)
        self.code = code
        self.padding = (UInt16Be(), UInt16Be(), UInt8())
        
    
class Negotiation(CompositeType):
    '''
    negociation request message
    '''
    def __init__(self, protocol = Protocols.PROTOCOL_SSL):
        CompositeType.__init__(self)
        self.flag = UInt8(0)
        #always 8
        self.len = UInt16Le(0x0008)
        self.protocol = protocol

class TPDU(LayerAutomata):
    '''
    TPDU layer management
    there is an connection automata
    '''
    def __init__(self, presentation = None):
        '''
        Constructor
        @param presentation: MCS layer
        '''
        LayerAutomata.__init__(self, presentation)
        
        #default protocol is SSl because is the only supported
        #in this version of RDPY
        self._protocol = Protocols.PROTOCOL_SSL
    
    def connect(self):
        '''
        connection request
        for client send a connection request packet
        '''
        self.sendConnectionRequest()
    
    def recvConnectionConfirm(self, data):
        '''
        recv connection confirm message
        next state is recvData 
        call connect on presentation layer if all is good
        @param data: Stream that contain connection confirm
        '''
        header = TPDUConnectHeader()
        data.readType(header)
        if header.code != MessageType.X224_TPDU_CONNECTION_CONFIRM:
            raise InvalidExpectedDataException("invalid TPDU header code X224_TPDU_CONNECTION_CONFIRM != %d"%header.code)
        #check presence of negotiation response
        if data.dataLen() == 8:
            self.readNeg(data)
        else:
            raise NegotiationFailure("server doesn't support SSL")
        
        self.setNextState(self.recvData)
        #connection is done send to presentation
        LayerAutomata.connect(self)
    
    def recvData(self, data):
        print "TPDU data"
        from rdpy.protocol.network.type import hexDump
        hexDump(data.getvalue())
        
    def sendConnectionRequest(self):
        '''
        write connection request message
        next state is recvConnectionConfirm
        '''
        neqReq = (NegociationType.TYPE_RDP_NEG_REQ, Negotiation(self._protocol))
        self._transport.send((TPDUConnectHeader(MessageType.X224_TPDU_CONNECTION_REQUEST, sizeof(neqReq)), neqReq))
        self.setNextState(self.recvConnectionConfirm)
        
    def send(self, message):
        '''
        write message packet for TPDU layer
        add TPDU header
        '''
        self._transport.send((UInt8(2), MessageType.X224_TPDU_DATA, UInt8(0x80), message))
        
    def readNeg(self, data):
        '''
        read negotiation response
        '''
        code = UInt8()
        data.readType(code)
        if code == NegociationType.TYPE_RDP_NEG_FAILURE:
            self.readNegFailure(data)
        elif code == NegociationType.TYPE_RDP_NEG_RSP:
            self.readNegResp(data)
        else:
            raise InvalidExpectedDataException("bad protocol negotiation response code")
    
    def readNegFailure(self, data):
        '''
        read negotiation failure packet
        '''
        print "Negotiation failure"
    
    def readNegResp(self, data):
        '''
        read negotiation response packet
        '''
        negResp = Negotiation()
        data.readType(negResp)
        
        if negResp.len != UInt16Le(0x0008):
            raise InvalidExpectedDataException("invalid size of negotiation response")
        
        self._protocol = negResp.protocol
        
        if self._protocol == Protocols.PROTOCOL_SSL:
            #_transport is TPKT and transport is TCP layer of twisted
            self._transport.transport.startTLS(ClientTLSContext())
        else:
            raise NegotiationFailure("protocol negociation failure")
        

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