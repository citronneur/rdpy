'''
@author: sylvain
'''

from rdpy.network.const import ConstAttributes, TypeAttributes
from rdpy.network.layer import LayerAutomata
from rdpy.network.type import sizeof, Stream, UInt8, UInt16Be
from rdpy.network.error import InvalidExpectedDataException, InvalidValue, InvalidSize
from rdpy.protocol.rdp.ber import writeLength

import ber, gcc, per

@ConstAttributes
@TypeAttributes(UInt8)
class Message(object):
    '''
    message type
    '''
    MCS_TYPE_CONNECT_INITIAL = 0x65
    MCS_TYPE_CONNECT_RESPONSE = 0x66

@ConstAttributes
@TypeAttributes(UInt8)
class DomainMCSPDU:
    '''
    domain mcs pdu header
    '''
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
    MCS_GLOBAL_CHANNEL = 1003
    MCS_USERCHANNEL_BASE = 1001

class MCS(LayerAutomata):
    '''
    Multi Channel Service layer
    the main layer of RDP protocol
    is why he can do everything and more!
    '''
    def __init__(self, presentation):
        '''
        ctor call base class ctor
        @param presentation: presentation layer
        '''
        LayerAutomata.__init__(self, presentation._mode, presentation)
        self._clientSettings = gcc.ClientSettings()
        self._serverSettings = gcc.ServerSettings()
        #default user Id
        self._userId = UInt16Be(1)
        #list of channel use in this layer and connection state
        self._channelIds = {Channel.MCS_GLOBAL_CHANNEL: presentation}
        #use to record already requested channel
        self._channelIdsRequest = {}
    
    def connect(self):
        '''
        connection send for client mode
        a write connect initial packet
        '''
        self._clientSettings.core.serverSelectedProtocol = self._transport._selectedProtocol
        self.sendConnectInitial()
        
    def connectNextChannel(self):
        '''
        send sendChannelJoinRequest message on next unconnect channel
        '''
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
                layer._transport = self
                layer._channelId = channelId
                layer.connect()
                
    def sendConnectInitial(self):
        '''
        send connect initial packet
        '''
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
        '''
        send a formated erect domain request for RDP connection
        '''
        self._transport.send((self.writeMCSPDUHeader(DomainMCSPDU.ERECT_DOMAIN_REQUEST), per.writeInteger(0), per.writeInteger(0)))
        
    def sendAttachUserRequest(self):
        '''
        send a formated attach user request for RDP connection
        '''
        self._transport.send(self.writeMCSPDUHeader(DomainMCSPDU.ATTACH_USER_REQUEST))
        
    def sendChannelJoinRequest(self, channelId):
        '''
        send a formated Channel join request from client to server
        '''
        self._transport.send((self.writeMCSPDUHeader(DomainMCSPDU.CHANNEL_JOIN_REQUEST), self._userId, channelId))
        
    def recvConnectResponse(self, data):
        '''
        receive mcs connect response from server
        @param data: Stream
        '''
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
        '''
        receive an attach user confirm
        @param data: Stream
        '''
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
        self._channelIds[self._userId + Channel.MCS_USERCHANNEL_BASE] = None#TODO + [(x, False) for x in self._serverSettings.channelsId])
        
        self.connectNextChannel()
    
    def recvChannelJoinConfirm(self, data):
        '''
        receive a channel join confirm from server
        @param data: Stream
        '''
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
        '''
        main receive method
        @param data: Stream 
        '''
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
        '''
        specific send function for channelId
        @param data: message to send
        '''
        self._transport.send((self.writeMCSPDUHeader(DomainMCSPDU.SEND_DATA_REQUEST), self._userId, channelId, UInt8(0x70), UInt16Be(sizeof(data)) | UInt16Be(0x8000), data))
        
    
    def writeDomainParams(self, maxChannels, maxUsers, maxTokens, maxPduSize):
        '''
        write a special domain param structure
        use in connection sequence
        @param maxChannels: number of mcs channel use
        @param maxUsers: number of mcs user used (1)
        @param maxTokens: unknown
        @param maxPduSize: unknown
        @return: domain param structure
        '''
        domainParam = (ber.writeInteger(maxChannels), ber.writeInteger(maxUsers), ber.writeInteger(maxTokens),
                       ber.writeInteger(1), ber.writeInteger(0), ber.writeInteger(1),
                       ber.writeInteger(maxPduSize), ber.writeInteger(2))
        return (ber.writeUniversalTag(ber.Tag.BER_TAG_SEQUENCE, True), writeLength(sizeof(domainParam)), domainParam)
    
    def writeMCSPDUHeader(self, mcsPdu, options = 0):
        '''
        write mcs pdu header
        @param mcsPdu: pdu code
        @param options: option contains in header
        @return: UInt8
        '''
        return (mcsPdu << 2) | options
    
    def readMCSPDUHeader(self, opcode, mcsPdu):
        '''
        read mcsPdu header and return options parameter
        @param opcode: UInt8 opcode
        @param mcsPdu: mcsPdu will be checked
        @return: true if opcode is correct
        '''
        return (opcode >> 2) == mcsPdu
    
    def readDomainParams(self, s):
        '''
        read domain params structure
        @return: (max_channels, max_users, max_tokens, max_pdu_size)
        '''
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
        
        