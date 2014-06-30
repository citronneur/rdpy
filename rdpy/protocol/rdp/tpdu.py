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
Implement transport PDU layer

This layer have main goal to negociate SSL transport
RDP basic security is not supported by RDPY (because is not a true security layer...)
"""

from rdpy.network.layer import LayerAutomata, LayerMode, StreamSender
from rdpy.network.type import UInt8, UInt16Le, UInt16Be, UInt32Le, CompositeType, sizeof
from rdpy.network.error import InvalidExpectedDataException

class MessageType(object):
    """
    Message type
    """
    X224_TPDU_CONNECTION_REQUEST = 0xE0
    X224_TPDU_CONNECTION_CONFIRM = 0xD0
    X224_TPDU_DISCONNECT_REQUEST = 0x80
    X224_TPDU_DATA = 0xF0
    X224_TPDU_ERROR = 0x70

class NegociationType(object):
    """
    Negotiation header
    """
    TYPE_RDP_NEG_REQ = 0x01
    TYPE_RDP_NEG_RSP = 0x02
    TYPE_RDP_NEG_FAILURE = 0x03

class Protocols(object):
    """
    Protocols available for TPDU layer
    """
    PROTOCOL_RDP = 0x00000000
    PROTOCOL_SSL = 0x00000001
    PROTOCOL_HYBRID = 0x00000002
    PROTOCOL_HYBRID_EX = 0x00000008
        
class NegotiationFailureCode(object):
    """
    Protocol negotiation failure code
    """
    SSL_REQUIRED_BY_SERVER = 0x00000001
    SSL_NOT_ALLOWED_BY_SERVER = 0x00000002
    SSL_CERT_NOT_ON_SERVER = 0x00000003
    INCONSISTENT_FLAGS = 0x00000004
    HYBRID_REQUIRED_BY_SERVER = 0x00000005
    SSL_WITH_USER_AUTH_REQUIRED_BY_SERVER = 0x00000006
    
class TPDUConnectMessage(CompositeType):
    """
    Header of TPDU connection messages 
    """
    def __init__(self, code):
        """
        @param code: MessageType
        """
        CompositeType.__init__(self)
        self.len = UInt8(lambda:sizeof(self) - 1)
        self.code = UInt8(code, constant = True)
        self.padding = (UInt16Be(), UInt16Be(), UInt8())
        #read if there is enough data
        self.protocolNeg = Negotiation(optional = True)
        
class TPDUDataHeader(CompositeType):
    """
    Header send when TPDU exchange application data
    """
    def __init__(self):
        CompositeType.__init__(self)
        self.header = UInt8(2, constant = True)
        self.messageType = UInt8(MessageType.X224_TPDU_DATA, constant = True)
        self.separator = UInt8(0x80, constant = True)
    
class Negotiation(CompositeType):
    """
    Negociate request message
    @see: request -> http://msdn.microsoft.com/en-us/library/cc240500.aspx
    @see: response -> http://msdn.microsoft.com/en-us/library/cc240506.aspx
    @see: failure ->http://msdn.microsoft.com/en-us/library/cc240507.aspx
    """
    def __init__(self, optional = False):
        CompositeType.__init__(self, optional = optional)
        self.code = UInt8()
        self.flag = UInt8(0)
        #always 8
        self.len = UInt16Le(0x0008, constant = True)
        self.selectedProtocol = UInt32Le(conditional = lambda: (self.code.value != NegociationType.TYPE_RDP_NEG_FAILURE))
        self.failureCode = UInt32Le(conditional = lambda: (self.code.value == NegociationType.TYPE_RDP_NEG_FAILURE))

class TPDU(LayerAutomata, StreamSender):
    """
    TPDU layer management
    there is an connection automata
    """
    def __init__(self, mode, presentation):
        """
        @param mode: automata mode (client or server)
        @param presentation: upper layer, MCS layer in RDP case
        """
        LayerAutomata.__init__(self, mode, presentation)
        #default selectedProtocol is SSl because is the only supported
        #in this version of RDPY
        #client requested selectedProtocol
        self._requestedProtocol = Protocols.PROTOCOL_SSL
        #server selected selectedProtocol
        self._selectedProtocol = Protocols.PROTOCOL_SSL
        
        #Server mode informations for TLS connection
        self._serverPrivateKeyFileName = None
        self._serverCertificateFileName = None
    
    def initTLSServerInfos(self, privateKeyFileName, certificateFileName):
        """
        Initialize informations for SSL server connection
        @param privateKeyFileName: file contain server private key
        @param certficiateFileName: file that contain public key
        """
        self._serverPrivateKeyFileName = privateKeyFileName
        self._serverCertificateFileName = certificateFileName
    
    def connect(self):
        """
        connection request
        for client send a connection request packet
        """
        if self._mode == LayerMode.CLIENT:
            self.sendConnectionRequest()
        else:
            self.setNextState(self.recvConnectionRequest)
    
    def recvConnectionConfirm(self, data):
        """
        receive connection confirm message
        next state is recvData 
        call connect on presentation layer if all is good
        @param data: Stream that contain connection confirm
        @see: response -> http://msdn.microsoft.com/en-us/library/cc240506.aspx
        @see: failure ->http://msdn.microsoft.com/en-us/library/cc240507.aspx
        """
        message = TPDUConnectMessage(MessageType.X224_TPDU_CONNECTION_CONFIRM)
        data.readType(message)
        
        #check presence of negotiation response
        if not message.protocolNeg._is_readed:
            raise InvalidExpectedDataException("server must support negotiation protocol to use SSL")
        
        if message.protocolNeg.failureCode._is_readed:
            raise InvalidExpectedDataException("negotiation failure code %x"%message.protocolNeg.failureCode.value)
        
        self._selectedProtocol = message.protocolNeg.selectedProtocol.value
        
        if self._selectedProtocol != Protocols.PROTOCOL_SSL:
            raise InvalidExpectedDataException("only ssl protocol is supported in RDPY version")
        
        #_transport is TPKT and transport is TCP layer of twisted
        self._transport.transport.startTLS(ClientTLSContext())
        
        self.setNextState(self.recvData)
        #connection is done send to presentation
        LayerAutomata.connect(self)
        
    def recvConnectionRequest(self, data):
        """
        Read connection confirm packet
        Next state is send connection confirm
        @param data: Stream
        @see : http://msdn.microsoft.com/en-us/library/cc240470.aspx
        """
        message = TPDUConnectMessage(MessageType.X224_TPDU_CONNECTION_REQUEST)
        data.readType(message)
        
        if not message.protocolNeg._is_readed or message.protocolNeg.failureCode._is_readed:
            raise InvalidExpectedDataException("Too older RDP client")
        
        self._requestedProtocol = message.protocolNeg.selectedProtocol.value
        
        if not self._requestedProtocol & Protocols.PROTOCOL_SSL:
            #send error message and quit
            message = TPDUConnectMessage()
            message.code.value = MessageType.X224_TPDU_CONNECTION_CONFIRM
            message.protocolNeg.code.value = NegociationType.TYPE_RDP_NEG_FAILURE
            message.protocolNeg.failureCode.value = NegotiationFailureCode.SSL_REQUIRED_BY_SERVER
            self._transport.send(message)
            raise InvalidExpectedDataException("rdpy needs ssl client compliant")
        
        self._selectedProtocol = Protocols.PROTOCOL_SSL
        self.sendConnectionConfirm()
    
    def recvData(self, data):
        """
        Read data header from packet
        And pass to presentation layer
        @param data: Stream
        """
        header = TPDUDataHeader()
        data.readType(header)
        self._presentation.recv(data)
        
    def sendConnectionRequest(self):
        """
        Write connection request message
        Next state is recvConnectionConfirm
        @see: http://msdn.microsoft.com/en-us/library/cc240500.aspx
        """
        message = TPDUConnectMessage(MessageType.X224_TPDU_CONNECTION_REQUEST)
        message.protocolNeg.code.value = NegociationType.TYPE_RDP_NEG_REQ
        message.protocolNeg.selectedProtocol.value = self._requestedProtocol
        self._transport.send(message)
        self.setNextState(self.recvConnectionConfirm)
        
    def sendConnectionConfirm(self):
        """
        Write connection confirm message
        Next state is recvData
        @see : http://msdn.microsoft.com/en-us/library/cc240501.aspx
        """
        message = TPDUConnectMessage(MessageType.X224_TPDU_CONNECTION_CONFIRM)
        message.protocolNeg.code.value = NegociationType.TYPE_RDP_NEG_REQ
        message.protocolNeg.selectedProtocol.value = self._selectedProtocol
        self._transport.send(message)
        #_transport is TPKT and transport is TCP layer of twisted
        self._transport.transport.startTLS(ServerTLSContext(self._serverPrivateKeyFileName, self._serverCertificateFileName))
        #connection is done send to presentation
        LayerAutomata.connect(self)
        
    def send(self, message):
        """
        Write message packet for TPDU layer
        Add TPDU header
        @param message: network.Type message
        """
        self._transport.send((TPDUDataHeader(), message))
        
def createClient(presentation):
    """
    Factory of TPDU layer in Client mode
    @param presentation: presentation layer, in RDP mode is MCS layer
    """
    return TPDU(LayerMode.CLIENT, presentation)

def createServer(presentation, privateKeyFileName, certificateFileName):
    """
    Factory of TPDU layer in Server mode
    @param privateKeyFileName: file contain server private key
    @param certficiateFileName: file that contain publi key
    """
    tpdu = TPDU(LayerMode.SERVER, presentation)
    tpdu.initTLSServerInfos(privateKeyFileName, certificateFileName)
    return tpdu

#open ssl needed
from twisted.internet import ssl
from OpenSSL import SSL

class ClientTLSContext(ssl.ClientContextFactory):
    """
    client context factory for open ssl
    """
    def getContext(self):
        context = SSL.Context(SSL.TLSv1_METHOD)
        context.set_options(0x00020000)#SSL_OP_NO_COMPRESSION
        context.set_options(SSL.OP_DONT_INSERT_EMPTY_FRAGMENTS)
        context.set_options(SSL.OP_TLS_BLOCK_PADDING_BUG)
        return context
    
class ServerTLSContext(ssl.DefaultOpenSSLContextFactory):
    """
    Server context factory for open ssl
    @param privateKeyFileName: Name of a file containing a private key
    @param certificateFileName: Name of a file containing a certificate
    """
    def __init__(self, privateKeyFileName, certificateFileName):
        ssl.DefaultOpenSSLContextFactory.__init__(self, privateKeyFileName, certificateFileName, SSL.TLSv1_METHOD)