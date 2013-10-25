'''
@author: sylvain
'''

from rdpy.utils.const import ConstAttributes, TypeAttributes
from rdpy.protocol.network.layer import LayerAutomata
from rdpy.protocol.network.type import sizeof, Stream, UInt8
from rdpy.protocol.rdp.ber import writeLength
from rdpy.protocol.network.error import InvalidExpectedDataException, InvalidValue, InvalidSize

import ber, gcc

@ConstAttributes
@TypeAttributes(UInt8)
class Message(object):
    '''
    message type
    '''
    MCS_TYPE_CONNECT_INITIAL = 0x65
    MCS_TYPE_CONNECT_RESPONSE = 0x66
    MCS_EDRQ = 1
    MCS_DPUM = 8
    MCS_AURQ = 10
    MCS_AUCF = 11
    MCS_CJRQ = 14
    MCS_CJCF = 15
    MCS_SDRQ = 25
    MCS_SDIN = 26
    
class Channel:
    MCS_GLOBAL_CHANNEL = 1003
    MCS_USERCHANNEL_BASE = 1001

class MCS(LayerAutomata):
    '''
    Multi Channel Service layer
    the main layer of RDP protocol
    is why he can do everything and more!
    '''
    
    def __init__(self, presentation = None):
        '''
        ctor call base class ctor
        @param presentation: presentation layer
        '''
        LayerAutomata.__init__(self, presentation)
        self._clientSettings = gcc.ClientSettings()
    
    def connect(self):
        '''
        connection send for client mode
        a write connect initial packet
        '''
        self._clientSettings.core.serverSelectedProtocol = self._transport._protocol
        self.sendConnectInitial()
    
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
    
    def readDomainParams(self, s):
        '''
        read domain params structure
        '''
        if not ber.readUniversalTag(s, ber.Tag.BER_TAG_SEQUENCE, True):
            raise InvalidValue("bad BER tags")
        length = ber.readLength(s)
        max_channels = ber.readInteger(s)
        max_users = ber.readInteger(s)
        max_tokens = ber.readInteger(s)
        ber.readInteger(s)
        ber.readInteger(s)
        ber.readInteger(s)
        max_pdu_size = ber.readInteger(s)
        ber.readInteger(s)
        
    def recvConnectResponse(self, data):
        ber.readApplicationTag(data, Message.MCS_TYPE_CONNECT_RESPONSE)
        ber.readEnumerated(data)
        ber.readInteger(data)
        self.readDomainParams(data)
        if not ber.readUniversalTag(data, ber.Tag.BER_TAG_OCTET_STRING, False):
            raise InvalidExpectedDataException("invalid expected tag")
        gccRequestLength = ber.readLength(data)
        if data.dataLen() != gccRequestLength:
            raise InvalidSize("gcc request have ")
        from rdpy.protocol.network.type import hexDump
        hexDump(data.getvalue())
        
        