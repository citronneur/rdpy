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

from rdpy.network.layer import LayerAutomata, IStreamSender
from rdpy.network.type import UInt8, UInt16Le, UInt16Be, UInt32Le, CompositeType, sizeof, String
from rdpy.base.error import InvalidExpectedDataException

class MessageType(object):
    """
    @summary: Message type
    """
    X224_TPDU_CONNECTION_REQUEST = 0xE0
    X224_TPDU_CONNECTION_CONFIRM = 0xD0
    X224_TPDU_DISCONNECT_REQUEST = 0x80
    X224_TPDU_DATA = 0xF0
    X224_TPDU_ERROR = 0x70

class NegociationType(object):
    """
    @summary: Negotiation header
    """
    TYPE_RDP_NEG_REQ = 0x01
    TYPE_RDP_NEG_RSP = 0x02
    TYPE_RDP_NEG_FAILURE = 0x03

class Protocols(object):
    """
    @summary: Protocols available for x224 layer
    """
    PROTOCOL_RDP = 0x00000000
    PROTOCOL_SSL = 0x00000001
    PROTOCOL_HYBRID = 0x00000002
    PROTOCOL_HYBRID_EX = 0x00000008
        
class NegotiationFailureCode(object):
    """
    @summary: Protocol negotiation failure code
    """
    SSL_REQUIRED_BY_SERVER = 0x00000001
    SSL_NOT_ALLOWED_BY_SERVER = 0x00000002
    SSL_CERT_NOT_ON_SERVER = 0x00000003
    INCONSISTENT_FLAGS = 0x00000004
    HYBRID_REQUIRED_BY_SERVER = 0x00000005
    SSL_WITH_USER_AUTH_REQUIRED_BY_SERVER = 0x00000006
    
class ClientConnectionRequestPDU(CompositeType):
    """
    @summary:  Connection request
                client -> server
    @see: http://msdn.microsoft.com/en-us/library/cc240470.aspx
    """
    def __init__(self):
        CompositeType.__init__(self)
        self.len = UInt8(lambda:sizeof(self) - 1)
        self.code = UInt8(MessageType.X224_TPDU_CONNECTION_REQUEST, constant = True)
        self.padding = (UInt16Be(), UInt16Be(), UInt8())
        self.cookie = String(until = "\x0d\x0a", conditional = lambda:(self.len._is_readed and self.len.value > 14))
        #read if there is enough data
        self.protocolNeg = Negotiation(optional = True)

class ServerConnectionConfirm(CompositeType):
    """
    @summary: Server response
    @see: http://msdn.microsoft.com/en-us/library/cc240506.aspx
    """
    def __init__(self):
        CompositeType.__init__(self)
        self.len = UInt8(lambda:sizeof(self) - 1)
        self.code = UInt8(MessageType.X224_TPDU_CONNECTION_CONFIRM, constant = True)
        self.padding = (UInt16Be(), UInt16Be(), UInt8())
        #read if there is enough data
        self.protocolNeg = Negotiation(optional = True)
        
class X224DataHeader(CompositeType):
    """
    @summary: Header send when x224 exchange application data
    """
    def __init__(self):
        CompositeType.__init__(self)
        self.header = UInt8(2)
        self.messageType = UInt8(MessageType.X224_TPDU_DATA, constant = True)
        self.separator = UInt8(0x80, constant = True)
    
class Negotiation(CompositeType):
    """
    @summary: Negociate request message
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

class X224Layer(LayerAutomata, IStreamSender):
    """
    @summary:  x224 layer management
                there is an connection automata
    """
    def __init__(self, presentation):
        """
        @param presentation: upper layer, MCS layer in RDP case
        """
        LayerAutomata.__init__(self, presentation)
        #default selectedProtocol is SSl because is the only supported
        #in this version of RDPY
        #client requested selectedProtocol
        self._requestedProtocol = Protocols.PROTOCOL_SSL
        #server selected selectedProtocol
        self._selectedProtocol = Protocols.PROTOCOL_SSL
    
    def recvData(self, data):
        """
        @summary: Read data header from packet
                   And pass to presentation layer
        @param data: Stream
        """
        header = X224DataHeader()
        data.readType(header)
        self._presentation.recv(data)
        
    def send(self, message):
        """
        @summary: Write message packet for TPDU layer
                   Add TPDU header
        @param message: network.Type message
        """
        self._transport.send((X224DataHeader(), message))
        
class Client(X224Layer):
    """
    @summary: Client automata of TPDU layer
    """
    def __init__(self, presentation):
        """
        @param presentation: upper layer, MCS layer in RDP case
        """
        X224Layer.__init__(self, presentation)
        
    def connect(self):
        """
        @summary: Connection request for client send a connection request packet
        """
        self.sendConnectionRequest()
        
    def sendConnectionRequest(self):
        """
        @summary:  Write connection request message
                    Next state is recvConnectionConfirm
        @see: http://msdn.microsoft.com/en-us/library/cc240500.aspx
        """
        message = ClientConnectionRequestPDU()
        message.protocolNeg.code.value = NegociationType.TYPE_RDP_NEG_REQ
        message.protocolNeg.selectedProtocol.value = self._requestedProtocol
        self._transport.send(message)
        self.setNextState(self.recvConnectionConfirm)
        
    def recvConnectionConfirm(self, data):
        """
        @summary:  Receive connection confirm message
                    Next state is recvData 
                    Call connect on presentation layer if all is good
        @param data: Stream that contain connection confirm
        @see: response -> http://msdn.microsoft.com/en-us/library/cc240506.aspx
        @see: failure ->http://msdn.microsoft.com/en-us/library/cc240507.aspx
        """
        message = ServerConnectionConfirm()
        data.readType(message)
        
        #check presence of negotiation response
        if not message.protocolNeg._is_readed:
            raise InvalidExpectedDataException("server must support negotiation protocol to use SSL")
        
        if message.protocolNeg.failureCode._is_readed:
            raise InvalidExpectedDataException("negotiation failure code %x"%message.protocolNeg.failureCode.value)
        
        self._selectedProtocol = message.protocolNeg.selectedProtocol.value
        
        if self._selectedProtocol != Protocols.PROTOCOL_SSL:
            raise InvalidExpectedDataException("only SSL protocol is supported in RDPY version")
        
        #_transport is TPKT and transport is TCP layer of twisted
        self._transport.transport.startTLS(ClientTLSContext())
        
        #now i'm ready to receive data
        self.setNextState(self.recvData)
        
        #connection is done send to presentation
        self._presentation.connect()

class Server(X224Layer):
    """
    @summary: Server automata of X224 layer
    """
    def __init__(self, presentation, privateKeyFileName, certificateFileName):
        """
        @param presentation: upper layer, MCS layer in RDP case
        @param privateKeyFileName: file contain server private key
        @param certficiateFileName: file that contain public key
        """
        X224Layer.__init__(self, presentation)
        #Server mode informations for TLS connection
        self._serverPrivateKeyFileName = privateKeyFileName
        self._serverCertificateFileName = certificateFileName
        
    def connect(self):
        """
        @summary: Connection request for server wait connection request packet from client
        """
        self.setNextState(self.recvConnectionRequest)
        
    def recvConnectionRequest(self, data):
        """
        @summary:  Read connection confirm packet
                    Next state is send connection confirm
        @param data: Stream
        @see : http://msdn.microsoft.com/en-us/library/cc240470.aspx
        """
        message = ClientConnectionRequestPDU()
        data.readType(message)
        
        if not message.protocolNeg._is_readed or message.protocolNeg.failureCode._is_readed:
            raise InvalidExpectedDataException("Too older RDP client")
        
        self._requestedProtocol = message.protocolNeg.selectedProtocol.value
        
        if not self._requestedProtocol & Protocols.PROTOCOL_SSL:
            #send error message and quit
            message = ServerConnectionConfirm()
            message.protocolNeg.code.value = NegociationType.TYPE_RDP_NEG_FAILURE
            message.protocolNeg.failureCode.value = NegotiationFailureCode.SSL_REQUIRED_BY_SERVER
            self._transport.send(message)
            raise InvalidExpectedDataException("rdpy needs ssl client compliant")
        
        self._selectedProtocol = Protocols.PROTOCOL_SSL
        self.sendConnectionConfirm()
        
    def sendConnectionConfirm(self):
        """
        @summary:  Write connection confirm message
                    Start TLS connection
                    Next state is recvData
        @see : http://msdn.microsoft.com/en-us/library/cc240501.aspx
        """
        message = ServerConnectionConfirm()
        message.protocolNeg.code.value = NegociationType.TYPE_RDP_NEG_RSP
        message.protocolNeg.selectedProtocol.value = self._selectedProtocol
        self._transport.send(message)
        #_transport is TPKT and transport is TCP layer of twisted
        self._transport.transport.startTLS(ServerTLSContext(self._serverPrivateKeyFileName, self._serverCertificateFileName))
        #connection is done send to presentation
        self.setNextState(self.recvData)
        self._presentation.connect()

#open ssl needed
from twisted.internet import ssl
from OpenSSL import SSL

class ClientTLSContext(ssl.ClientContextFactory):
    """
    @summary: client context factory for open ssl
    """
    def getContext(self):
        context = SSL.Context(SSL.TLSv1_METHOD)
        context.set_options(SSL.OP_DONT_INSERT_EMPTY_FRAGMENTS)
        context.set_options(SSL.OP_TLS_BLOCK_PADDING_BUG)
        return context
    
class ServerTLSContext(ssl.DefaultOpenSSLContextFactory):
    """
    @summary: Server context factory for open ssl
    @param privateKeyFileName: Name of a file containing a private key
    @param certificateFileName: Name of a file containing a certificate
    """
    def __init__(self, privateKeyFileName, certificateFileName):
        class TPDUSSLContext(SSL.Context):
            def __init__(self, method):
                SSL.Context.__init__(self, method)
                self.set_options(SSL.OP_DONT_INSERT_EMPTY_FRAGMENTS)
                self.set_options(SSL.OP_TLS_BLOCK_PADDING_BUG)

        ssl.DefaultOpenSSLContextFactory.__init__(self, privateKeyFileName, certificateFileName, SSL.SSLv23_METHOD, TPDUSSLContext)
        