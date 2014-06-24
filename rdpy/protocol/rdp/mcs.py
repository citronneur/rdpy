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
Implement Multi Channel Service

Each channel have a particular role.
The main channel is the graphical channel.
It exist channel for file system order, audio channel, clipboard etc...
"""

from rdpy.network.const import ConstAttributes, TypeAttributes
from rdpy.network.layer import LayerAutomata, LayerMode, StreamSender
from rdpy.network.type import sizeof, Stream, UInt8, UInt16Be
from rdpy.network.error import InvalidExpectedDataException, InvalidValue, InvalidSize
from rdpy.protocol.rdp.ber import writeLength

import ber, gcc, per

@ConstAttributes
@TypeAttributes(UInt8)
class Message(object):
    """
    Message type
    """
    MCS_TYPE_CONNECT_INITIAL = 0x65
    MCS_TYPE_CONNECT_RESPONSE = 0x66

@ConstAttributes
@TypeAttributes(UInt8)
class DomainMCSPDU:
    """
    Domain MCS PDU header
    """
    ERECT_DOMAIN_REQUEST = 1
    DISCONNECT_PROVIDER_ULTIMATUM = 8
    ATTACH_USER_REQUEST = 10
    ATTACH_USER_CONFIRM = 11
    CHANNEL_JOIN_REQUEST = 14
    CHANNEL_JOIN_CONFIRM = 15
    SEND_DATA_REQUEST = 25
    SEND_DATA_INDICATION = 26

@ConstAttributes
@TypeAttributes(UInt16Be)
class Channel:
    """
    Channel id of main channels use in RDP
    """
    MCS_GLOBAL_CHANNEL = 1003
    MCS_USERCHANNEL_BASE = 1001

class MCS(LayerAutomata):
    """
    Multi Channel Service layer
    the main layer of RDP protocol
    is why he can do everything and more!
    """
    class MCSProxySender(StreamSender):
        """
        Proxy use to set as transport layer for upper channel
        use to abstract channel id for presentation layer
        """
        def __init__(self, mcs, channelId):
            """
            @param mcs: MCS layer use as proxy
            @param channelId: channel id for presentation layer 
            """
            self._mcs = mcs
            self._channelId = channelId
            
        def send(self, data):
            '''
            a send proxy function, use channel id and specific 
            send function of mcs layer
            '''
            self._mcs.send(self._channelId, data)
            
        def getUserId(self):
            '''
            @return: mcs user id
            '''
            return self._mcs._userId
        
        def getChannelId(self):
            '''
            @return: return channel id of proxy
            '''
            return self._channelId
            
        def getGCCClientSettings(self):
            '''
            @return: mcs layer gcc client settings
            '''
            return self._mcs._clientSettings
        
        def getGCCServerSettings(self):
            '''
            @return: mcs layer gcc server settings
            '''
            return self._mcs._serverSettings
        
    
    def __init__(self, mode, presentation):
        """
        @param mode: mode of MCS layer
        @param presentation: presentation layer
        """
        LayerAutomata.__init__(self, mode, presentation)
        self._clientSettings = gcc.ClientSettings()
        self._serverSettings = gcc.ServerSettings()
        #default user Id
        self._userId = UInt16Be(1)
        #list of channel use in this layer and connection state
        self._channelIds = {Channel.MCS_GLOBAL_CHANNEL: presentation}
        #use to record already requested channel
        self._channelIdsRequest = {}
    
    def connect(self):
        """
        Connection send for client mode
        a write connect initial packet
        """
        self._clientSettings.core.serverSelectedProtocol = self._transport._selectedProtocol
        self.sendConnectInitial()
        
    def connectNextChannel(self):
        """
        Send sendChannelJoinRequest message on next unconnect channel
        """
        for (channelId, layer) in self._channelIds.iteritems():
            #for each unconnect channel send a request
            if not self._channelIdsRequest.has_key(channelId):
                self.sendChannelJoinRequest(channelId)
                self.setNextState(self.recvChannelJoinConfirm)
                return
            
        #connection is done reinit class
        self.setNextState(self.recvData)
        #try connection on all requested channel
        for (channelId, layer) in self._channelIds.iteritems():
            if self._channelIdsRequest[channelId] and not layer is None:
                #use proxy foreach channell
                layer._transport = MCS.MCSProxySender(self, channelId)
                layer.connect()
                
    def sendConnectInitial(self):
        """
        Send connect initial packet
        """
        ccReq = gcc.writeConferenceCreateRequest(self._clientSettings)
        ccReqStream = Stream()
        ccReqStream.writeType(ccReq)
        
        tmp = (ber.writeOctetstring("\x01"), ber.writeOctetstring("\x01"), ber.writeBoolean(True),
               self.writeDomainParams(34, 2, 0, 0xffff),
               self.writeDomainParams(1, 1, 1, 0x420),
               self.writeDomainParams(0xffff, 0xfc17, 0xffff, 0xffff),
               ber.writeOctetstring(ccReqStream.getvalue()))
        self._transport.send((ber.writeApplicationTag(Message.MCS_TYPE_CONNECT_INITIAL, sizeof(tmp)), tmp))
        #we must receive a connect response
        self.setNextState(self.recvConnectResponse)
        
    def sendErectDomainRequest(self):
        """
        Send a formated erect domain request for RDP connection
        """
        self._transport.send((self.writeMCSPDUHeader(DomainMCSPDU.ERECT_DOMAIN_REQUEST), per.writeInteger(0), per.writeInteger(0)))
        
    def sendAttachUserRequest(self):
        """
        Send a formated attach user request for RDP connection
        """
        self._transport.send(self.writeMCSPDUHeader(DomainMCSPDU.ATTACH_USER_REQUEST))
        
    def sendChannelJoinRequest(self, channelId):
        """
        Send a formated Channel join request from client to server
        """
        self._transport.send((self.writeMCSPDUHeader(DomainMCSPDU.CHANNEL_JOIN_REQUEST), self._userId, channelId))
        
    def recvConnectResponse(self, data):
        """
        receive MCS connect response from server
        @param data: Stream
        """
        ber.readApplicationTag(data, Message.MCS_TYPE_CONNECT_RESPONSE)
        ber.readEnumerated(data)
        ber.readInteger(data)
        self.readDomainParams(data)
        if not ber.readUniversalTag(data, ber.Tag.BER_TAG_OCTET_STRING, False):
            raise InvalidExpectedDataException("invalid expected ber tag")
        gccRequestLength = ber.readLength(data)
        if data.dataLen() != gccRequestLength:
            raise InvalidSize("bad size of gcc request")
        self._serverSettings = gcc.readConferenceCreateResponse(data)
        
        #send domain request
        self.sendErectDomainRequest()
        #send attach user request
        self.sendAttachUserRequest()
        #now wait user confirm from server
        self.setNextState(self.recvAttachUserConfirm)
        
    def recvAttachUserConfirm(self, data):
        """
        Receive an attach user confirm
        @param data: Stream
        """
        opcode = UInt8()
        confirm = UInt8()
        data.readType((opcode, confirm))
        if not self.readMCSPDUHeader(opcode, DomainMCSPDU.ATTACH_USER_CONFIRM):
            raise InvalidExpectedDataException("invalid MCS PDU")
        if confirm != 0:
            raise Exception("server reject user")
        if opcode & UInt8(2) == UInt8(2):
            data.readType(self._userId)
            
        #build channel list because we have user id
        #add default channel + channels accepted by gcc connection sequence
        self._channelIds[self._userId + Channel.MCS_USERCHANNEL_BASE] = None
        
        self.connectNextChannel()
    
    def recvChannelJoinConfirm(self, data):
        """
        Receive a channel join confirm from server
        @param data: Stream
        """
        opcode = UInt8()
        confirm = UInt8()
        data.readType((opcode, confirm))
        if not self.readMCSPDUHeader(opcode, DomainMCSPDU.CHANNEL_JOIN_CONFIRM):
            raise InvalidExpectedDataException("invalid MCS PDU")
        userId = UInt16Be()
        channelId = UInt16Be()
        data.readType((userId, channelId))
        #save state of channel
        self._channelIdsRequest[channelId] = confirm == 0
        if confirm == 0:
            print "server accept channel %d"%channelId.value
        else:
            print "server refused channel %d"%channelId.value
            
        self.connectNextChannel()
        
    def recvData(self, data):
        """
        Main receive method
        @param data: Stream 
        """
        opcode = UInt8()
        data.readType(opcode)
        
        if self.readMCSPDUHeader(opcode, DomainMCSPDU.DISCONNECT_PROVIDER_ULTIMATUM):
            print "receive DISCONNECT_PROVIDER_ULTIMATUM"
            self.close()
            
        elif not self.readMCSPDUHeader(opcode, DomainMCSPDU.SEND_DATA_INDICATION):
            raise InvalidExpectedDataException("invalid expected mcs opcode")
        
        userId = UInt16Be()
        channelId = UInt16Be()
        flags = UInt8()
        length = UInt8()
        
        data.readType((userId, channelId, flags, length))
        
        if length & UInt8(0x80) == UInt8(0x80):
            lengthP2 = UInt8()
            data.readType(lengthP2)
            length = UInt16Be(length.value & 0x7f << 8 | lengthP2.value)
        
        #channel id doesn't match a requested layer
        if not self._channelIdsRequest.has_key(channelId):
            print "receive data for an unrequested layer"
            return
        
        #channel id math an unconnected layer
        if not self._channelIdsRequest[channelId]:
            print "receive data for an unconnected layer"
            return
        
        self._channelIds[channelId].recv(data)
        
    def send(self, channelId, data):
        """
        Specific send function for channelId
        @param channelId: Channel use to send
        @param data: message to send
        """
        self._transport.send((self.writeMCSPDUHeader(DomainMCSPDU.SEND_DATA_REQUEST), self._userId, channelId, UInt8(0x70), UInt16Be(sizeof(data)) | UInt16Be(0x8000), data))
        
    
    def writeDomainParams(self, maxChannels, maxUsers, maxTokens, maxPduSize):
        """
        Write a special domain parameter structure
        use in connection sequence
        @param maxChannels: number of MCS channel use
        @param maxUsers: number of MCS user used (1)
        @param maxTokens: unknown
        @param maxPduSize: unknown
        @return: domain parameter structure
        """
        domainParam = (ber.writeInteger(maxChannels), ber.writeInteger(maxUsers), ber.writeInteger(maxTokens),
                       ber.writeInteger(1), ber.writeInteger(0), ber.writeInteger(1),
                       ber.writeInteger(maxPduSize), ber.writeInteger(2))
        return (ber.writeUniversalTag(ber.Tag.BER_TAG_SEQUENCE, True), writeLength(sizeof(domainParam)), domainParam)
    
    def writeMCSPDUHeader(self, mcsPdu, options = 0):
        """
        Write MCS PDU header
        @param mcsPdu: PDU code
        @param options: option contains in header
        @return: UInt8
        """
        return (mcsPdu << 2) | options
    
    def readMCSPDUHeader(self, opcode, mcsPdu):
        """
        Read mcsPdu header and return options parameter
        @param opcode: UInt8 opcode
        @param mcsPdu: mcsPdu will be checked
        @return: true if opcode is correct
        """
        return (opcode >> 2) == mcsPdu
    
    def readDomainParams(self, s):
        """
        Read domain parameters structure
        @return: (max_channels, max_users, max_tokens, max_pdu_size)
        """
        if not ber.readUniversalTag(s, ber.Tag.BER_TAG_SEQUENCE, True):
            raise InvalidValue("bad BER tags")
        ber.readLength(s)#length
        max_channels = ber.readInteger(s)
        max_users = ber.readInteger(s)
        max_tokens = ber.readInteger(s)
        ber.readInteger(s)
        ber.readInteger(s)
        ber.readInteger(s)
        max_pdu_size = ber.readInteger(s)
        ber.readInteger(s)
        return (max_channels, max_users, max_tokens, max_pdu_size)

def createClient(controller):
    """
    @param controller: RDP controller which initialized all channel layer
    @return: MCS layer in client mode
    """
    return MCS(LayerMode.CLIENT, controller.getPDULayer())

def createServer(controller):
    """
    @param controller: RDP controller which initialized all channel layer
    @return: MCS layer in server mode
    """
    return MCS(LayerMode.SERVER, controller.getPDULayer())
        