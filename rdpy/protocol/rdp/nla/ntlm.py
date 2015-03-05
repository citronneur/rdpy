#
# Copyright (c) 2014-2015 Sylvain Peyrefitte
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
@summary: NTLM Authentication
@see: https://msdn.microsoft.com/en-us/library/cc236621.aspx
"""

import hashlib, hmac, struct, datetime
import sspi
import rdpy.security.pyDes as pyDes
import rdpy.security.rc4 as rc4
from rdpy.security.rsa_wrapper import random
from rdpy.core.type import CompositeType, CallableValue, String, UInt8, UInt16Le, UInt24Le, UInt32Le, sizeof, Stream
from rdpy.core import filetimes

class MajorVersion(object):
    """
    @see: https://msdn.microsoft.com/en-us/library/cc236654.aspx
    @see: https://msdn.microsoft.com/en-us/library/a211d894-21bc-4b8b-86ba-b83d0c167b00#id29
    """
    WINDOWS_MAJOR_VERSION_5 = 0x05
    WINDOWS_MAJOR_VERSION_6 = 0x06
    
class MinorVersion(object):
    """
    @see: https://msdn.microsoft.com/en-us/library/cc236654.aspx
    @see: https://msdn.microsoft.com/en-us/library/a211d894-21bc-4b8b-86ba-b83d0c167b00#id30
    """
    WINDOWS_MINOR_VERSION_0 = 0x00
    WINDOWS_MINOR_VERSION_1 = 0x01
    WINDOWS_MINOR_VERSION_2 = 0x02
    WINDOWS_MINOR_VERSION_3 = 0x03
    
class NTLMRevision(object):
    """
    @see: https://msdn.microsoft.com/en-us/library/cc236654.aspx
    """
    NTLMSSP_REVISION_W2K3 = 0x0F
    
class Negotiate(object):
    """
    @see: https://msdn.microsoft.com/en-us/library/cc236650.aspx
    """
    NTLMSSP_NEGOTIATE_56 = 0x80000000
    NTLMSSP_NEGOTIATE_KEY_EXCH = 0x40000000
    NTLMSSP_NEGOTIATE_128 = 0x20000000
    NTLMSSP_NEGOTIATE_VERSION = 0x02000000
    NTLMSSP_NEGOTIATE_TARGET_INFO = 0x00800000
    NTLMSSP_REQUEST_NON_NT_SESSION_KEY = 0x00400000
    NTLMSSP_NEGOTIATE_IDENTIFY = 0x00100000
    NTLMSSP_NEGOTIATE_EXTENDED_SESSIONSECURITY = 0x00080000
    NTLMSSP_TARGET_TYPE_SERVER = 0x00020000
    NTLMSSP_TARGET_TYPE_DOMAIN = 0x00010000
    NTLMSSP_NEGOTIATE_ALWAYS_SIGN = 0x00008000
    NTLMSSP_NEGOTIATE_OEM_WORKSTATION_SUPPLIED = 0x00002000
    NTLMSSP_NEGOTIATE_OEM_DOMAIN_SUPPLIED = 0x00001000
    NTLMSSP_NEGOTIATE_NTLM = 0x00000200
    NTLMSSP_NEGOTIATE_LM_KEY = 0x00000080
    NTLMSSP_NEGOTIATE_DATAGRAM = 0x00000040
    NTLMSSP_NEGOTIATE_SEAL = 0x00000020
    NTLMSSP_NEGOTIATE_SIGN = 0x00000010
    NTLMSSP_REQUEST_TARGET = 0x00000004
    NTLM_NEGOTIATE_OEM = 0x00000002
    NTLMSSP_NEGOTIATE_UNICODE = 0x00000001
    
def getPayLoadField(message, length, bufferOffset):
        if length == 0:
            return None
        offset = sizeof(message) - sizeof(message.Payload)
        start = bufferOffset - offset
        end = start + length
        return message.Payload.value[start:end]

class Version(CompositeType):
    """
    @summary: Version structure as describe in NTLM spec
    @see: https://msdn.microsoft.com/en-us/library/cc236654.aspx
    """
    def __init__(self, conditional):
        CompositeType.__init__(self, conditional = conditional)
        self.ProductMajorVersion = UInt8(MajorVersion.WINDOWS_MAJOR_VERSION_6)
        self.ProductMinorVersion = UInt8(MinorVersion.WINDOWS_MINOR_VERSION_0)
        self.ProductBuild = UInt16Le(6002)
        self.Reserved = UInt24Le()
        self.NTLMRevisionCurrent = UInt8(NTLMRevision.NTLMSSP_REVISION_W2K3)
        
class MessageSignatureEx(CompositeType):
    """
    @summary: Signature for message
    @see: https://msdn.microsoft.com/en-us/library/cc422952.aspx
    """
    def __init__(self):
        CompositeType.__init__(self)
        self.Version = UInt32Le(0x00000001, constant = True)
        self.Checksum = String(readLen = CallableValue(16))
        self.SeqNum = UInt32Le()

class NegotiateMessage(CompositeType):
    """
    @summary: Message send from client to server to negotiate capability of NTLM Authentication
    @see: https://msdn.microsoft.com/en-us/library/cc236641.aspx
    """
    def __init__(self):
        CompositeType.__init__(self)
        self.Signature = String("NTLMSSP\x00", readLen = CallableValue(8), constant = True)
        self.MessageType = UInt32Le(0x00000001, constant = True)
        
        self.NegotiateFlags = UInt32Le()
        
        self.DomainNameLen = UInt16Le()
        self.DomainNameMaxLen = UInt16Le(lambda:self.DomainNameLen.value)
        self.DomainNameBufferOffset = UInt32Le()
        
        self.WorkstationLen = UInt16Le()
        self.WorkstationMaxLen = UInt16Le(lambda:self.WorkstationLen.value)
        self.WorkstationBufferOffset = UInt32Le()
        
        self.Version = Version(conditional = lambda:(self.NegotiateFlags.value & Negotiate.NTLMSSP_NEGOTIATE_VERSION))
        
        self.Payload = String()

class ChallengeMessage(CompositeType):
    """
    @summary: Message send from server to client contains server challenge
    @see: https://msdn.microsoft.com/en-us/library/cc236642.aspx
    """
    def __init__(self):
        CompositeType.__init__(self)
        self.Signature = String("NTLMSSP\x00", readLen = CallableValue(8), constant = True)
        self.MessageType = UInt32Le(0x00000002, constant = True)
        
        self.TargetNameLen = UInt16Le()
        self.TargetNameMaxLen = UInt16Le(lambda:self.TargetNameLen.value)
        self.TargetNameBufferOffset = UInt32Le()
        
        self.NegotiateFlags = UInt32Le()
        
        self.ServerChallenge = String(readLen = CallableValue(8))
        self.Reserved = String("\x00" * 8, readLen = CallableValue(8))
        
        self.TargetInfoLen = UInt16Le()
        self.TargetInfoMaxLen = UInt16Le(lambda:self.TargetInfoLen.value)
        self.TargetInfoBufferOffset = UInt32Le()
        
        self.Version = Version(conditional = lambda:(self.NegotiateFlags.value & Negotiate.NTLMSSP_NEGOTIATE_VERSION))
        self.Payload = String()
        
    def getTargetName(self):
        return getPayLoadField(self, self.TargetNameLen.value, self.TargetNameBufferOffset.value)
    
    def getTargetInfo(self):
        return getPayLoadField(self, self.TargetInfoLen.value - 4, self.TargetInfoBufferOffset.value)
        
class AuthenticateMessage(CompositeType):
    """
    @summary: Last message in ntlm authentication
    @see: https://msdn.microsoft.com/en-us/library/cc236643.aspx
    """
    def __init__(self):
        CompositeType.__init__(self)
        self.Signature = String("NTLMSSP\x00", readLen = CallableValue(8), constant = True)
        self.MessageType = UInt32Le(0x00000003, constant = True)
        
        self.LmChallengeResponseLen = UInt16Le()
        self.LmChallengeResponseMaxLen = UInt16Le(lambda:self.LmChallengeResponseLen.value)
        self.LmChallengeResponseBufferOffset = UInt32Le()
        
        self.NtChallengeResponseLen = UInt16Le()
        self.NtChallengeResponseMaxLen = UInt16Le(lambda:self.NtChallengeResponseLen.value)
        self.NtChallengeResponseBufferOffset = UInt32Le()
        
        self.DomainNameLen = UInt16Le()
        self.DomainNameMaxLen = UInt16Le(lambda:self.DomainNameLen.value)
        self.DomainNameBufferOffset = UInt32Le()
        
        self.UserNameLen = UInt16Le()
        self.UserNameMaxLen = UInt16Le(lambda:self.UserNameLen.value)
        self.UserNameBufferOffset = UInt32Le()
        
        self.WorkstationLen = UInt16Le()
        self.WorkstationMaxLen = UInt16Le(lambda:self.WorkstationLen.value)
        self.WorkstationBufferOffset = UInt32Le()
        
        self.EncryptedRandomSessionLen = UInt16Le()
        self.EncryptedRandomSessionMaxLen = UInt16Le(lambda:self.EncryptedRandomSessionLen.value)
        self.EncryptedRandomSessionBufferOffset = UInt32Le()
        
        self.NegotiateFlags = UInt32Le()
        self.Version = Version(conditional = lambda:(self.NegotiateFlags.value & Negotiate.NTLMSSP_NEGOTIATE_VERSION))
        
        #self.MIC = String("\x00" * 16, readLen = CallableValue(16))
        self.Payload = String()
        
    def getUserName(self):
        return getPayLoadField(self, self.UserNameLen.value, self.UserNameBufferOffset.value)
    
    def getDomainName(self):
        return getPayLoadField(self, self.DomainNameLen.value, self.DomainNameBufferOffset.value)
    
    def getLmChallengeResponse(self):
        return getPayLoadField(self, self.LmChallengeResponseLen.value, self.LmChallengeResponseBufferOffset.value)
    
    def getNtChallengeResponse(self):
        return getPayLoadField(self, self.NtChallengeResponseLen.value, self.NtChallengeResponseBufferOffset.value)
    
    def getEncryptedRandomSession(self):
        return getPayLoadField(self, self.EncryptedRandomSessionLen.value, self.EncryptedRandomSessionBufferOffset.value)

def createAuthenticationMessage(domain, user, NtChallengeResponse, LmChallengeResponse, EncryptedRandomSessionKey):
    """
    @summary: Create an Authenticate Message
    @param domain: {str} domain microsoft
    @param user: {str} user microsoft
    @param NtChallengeResponse: {str} Challenge response
    @param LmChallengeResponse: {str} domain microsoft
    @param EncryptedRandomSessionKey: {str} EncryptedRandomSessionKey
    """
    message = AuthenticateMessage()
    #fill message
    offset = sizeof(message)
    
    message.DomainNameLen.value = len(domain)
    message.DomainNameBufferOffset.value = offset
    message.Payload.value += domain
    offset += len(domain)
    
    message.UserNameLen.value = len(user)
    message.UserNameBufferOffset.value = offset
    message.Payload.value += user
    offset += len(user)
    
    message.LmChallengeResponseLen.value = len(LmChallengeResponse)
    message.LmChallengeResponseBufferOffset.value = offset
    message.Payload.value += LmChallengeResponse
    offset += len(LmChallengeResponse)
    
    message.NtChallengeResponseLen.value = len(NtChallengeResponse)
    message.NtChallengeResponseBufferOffset.value = offset
    message.Payload.value += NtChallengeResponse
    offset += len(NtChallengeResponse)
    
    message.EncryptedRandomSessionLen.value = len(EncryptedRandomSessionKey)
    message.EncryptedRandomSessionBufferOffset.value = offset
    message.Payload.value += EncryptedRandomSessionKey
    offset += len(EncryptedRandomSessionKey)
    
    return message

def expandDesKey(key):
    """
    @summary: Expand the key from a 7-byte password key into a 8-byte DES key
    """
    s = chr(((ord(key[0]) >> 1) & 0x7f) << 1)
    s = s + chr(((ord(key[0]) & 0x01) << 6 | ((ord(key[1]) >> 2) & 0x3f)) << 1)
    s = s + chr(((ord(key[1]) & 0x03) << 5 | ((ord(key[2]) >> 3) & 0x1f)) << 1)
    s = s + chr(((ord(key[2]) & 0x07) << 4 | ((ord(key[3]) >> 4) & 0x0f)) << 1)
    s = s + chr(((ord(key[3]) & 0x0f) << 3 | ((ord(key[4]) >> 5) & 0x07)) << 1)
    s = s + chr(((ord(key[4]) & 0x1f) << 2 | ((ord(key[5]) >> 6) & 0x03)) << 1)
    s = s + chr(((ord(key[5]) & 0x3f) << 1 | ((ord(key[6]) >> 7) & 0x01)) << 1)
    s = s + chr((ord(key[6]) & 0x7f) << 1)
    return s

def CurrentFileTimes():
    """
    @summary: Current File times in 64 bits
    @return  : {str[8]}
    """
    return struct.pack("Q", filetimes.dt_to_filetime(datetime.datetime.now()))

def DES(key, data):
    """
    @summary: DES use in microsoft specification
    @param key: {str}    Des key on 56 bits or 7 bytes
    @param data: {str}    data to encrypt
    """
    return pyDes.des(expandDesKey(key)).encrypt(data)

def DESL(key, data):
    """
    @summary: an krosoft security function (triple des = des + des + des ;-))
    @param key: {str} Des key
    @param data: {str} encrypted data
    """
    return DES(key[0:7], data) + DES(key[7:14], data) + DES(key[14:16] + "\x00" * 5, data)

def UNICODE(s):
    """
    @param s: source
    @return: {str} encoded in unicode
    """
    return s.encode('utf-16le')

def MD4(s):
    """
    @summary: compute the md4 sum
    @param s: {str} input data
    @return: {str} MD4(s)
    """
    return hashlib.new('md4', s).digest()

def MD5(s):
    """
    @summary: compute the md5 sum
    @param s: {str} input data
    @return: {str} MD5(s)
    """
    return hashlib.new('md5', s).digest()

def Z(m):
    """
    @summary: fill m zero in string
    @param m: {int} size of string
    @return: \x00 * m 
    """
    return "\x00" * m

def RC4K(key, plaintext):
    """
    @summary: Context free of rc4 encoding
    @param key: {str} key
    @param plaintext: {str} plaintext
    @return {str} encrypted text
    """
    return rc4.crypt(rc4.RC4Key(key), plaintext)

def KXKEYv2(SessionBaseKey, LmChallengeResponse, ServerChallenge):
    """
    @summary: Key eXchange Key for NTLMv2
    @param SessionBaseKey: {str} computed by NTLMv1Anthentication or NTLMv2Authenticate function
    @param LmChallengeResponse : {str} computed by NTLMv1Anthentication or NTLMv2Authenticate function
    @param ServerChallenge : {str} Server chanllenge come from ChallengeMessage
    @see: https://msdn.microsoft.com/en-us/library/cc236710.aspx
    """
    return SessionBaseKey

def SEALKEY(ExportedSessionKey, client):
    if client:
        return MD5(ExportedSessionKey + "session key to client-to-server sealing key magic constant\0")
    else:
        return MD5(ExportedSessionKey + "session key to server-to-client sealing key magic constant\0")

def SIGNKEY(ExportedSessionKey, client):
    if client:
        return MD5(ExportedSessionKey + "session key to client-to-server signing key magic constant\0")
    else:
        return MD5(ExportedSessionKey + "session key to server-to-client signing key magic constant\0")

def HMAC_MD5(key, data):
    """
    @summary: classic HMAC algorithm with MD5 sum
    @param key: {str} key
    @param data: {str} data
    """
    return hmac.new(key, data, hashlib.md5).digest()

def NTOWFv2(Passwd, User, UserDom):
    """
    @summary: Version 2 of NTLM hash function
    @param Passwd: {str} Password
    @param User: {str} Username
    @param UserDom: {str} microsoft domain
    @see: https://msdn.microsoft.com/en-us/library/cc236700.aspx
    """
    return HMAC_MD5(MD4(UNICODE(Passwd)), UNICODE(User.upper() + UserDom))

def LMOWFv2(Passwd, User, UserDom):
    """
    @summary: Same as NTOWFv2
    @param Passwd: {str} Password
    @param User: {str} Username
    @param UserDom: {str} microsoft domain
    @see: https://msdn.microsoft.com/en-us/library/cc236700.aspx
    """
    return NTOWFv2(Passwd, User, UserDom)

def ComputeResponsev2(ResponseKeyNT, ResponseKeyLM, ServerChallenge, ClientChallenge, Time, ServerName):
    """
    @summary: process NTLMv2 Authenticate hash
    @param NegFlg: {int} Negotiation flags come from challenge message
    @see: https://msdn.microsoft.com/en-us/library/cc236700.aspx
    """
    Responserversion = "\x01"
    HiResponserversion = "\x01"

    temp = Responserversion + HiResponserversion + Z(6) + Time + ClientChallenge + Z(4) + ServerName + Z(4)
    NTProofStr = HMAC_MD5(ResponseKeyNT, ServerChallenge + temp)
    NtChallengeResponse = NTProofStr + temp
    LmChallengeResponse = HMAC_MD5(ResponseKeyLM, ServerChallenge + ClientChallenge) + ClientChallenge
    
    SessionBaseKey = HMAC_MD5(ResponseKeyNT, NTProofStr)
    
    return NtChallengeResponse, LmChallengeResponse, SessionBaseKey

def MAC(handle, SigningKey, SeqNum, Message):
    """
    @summary: generate signature for application message
    @param handle: {rc4.RC4Key} handle on crypt
    @param SigningKey: {str} Signing key
    @param SeqNum: {int} Sequence number
    @param Message: Message to sign
    @see: https://msdn.microsoft.com/en-us/library/cc422952.aspx
    """
    signature = MessageSignatureEx()
    signature.SeqNum.value = SeqNum
    
    #write the SeqNum
    s = Stream()
    s.writeType(signature.SeqNum)
    
    signature.Checksum.value = rc4.crypt(handle, HMAC_MD5(SigningKey, s.getvalue() + Message)[:8])
    
    return signature
    
class NTLMv2(sspi.IAuthenticationProtocol):
    """
    @summary: Handle NTLMv2 Authentication
    """
    def __init__(self, domain, user, password):
        self._domain = domain
        self._user = user
        #https://msdn.microsoft.com/en-us/library/cc236700.aspx
        self._ResponseKeyNT = NTOWFv2(password, user, domain)
        self._ResponseKeyLM = LMOWFv2(password, user, domain)
    
    def getNegotiateMessage(self):
        """
        @summary: generate first handshake messgae
        """
        message = NegotiateMessage()
        message.NegotiateFlags.value = (Negotiate.NTLMSSP_NEGOTIATE_KEY_EXCH |
                                        Negotiate.NTLMSSP_NEGOTIATE_128 |
                                        Negotiate.NTLMSSP_NEGOTIATE_EXTENDED_SESSIONSECURITY |
                                        Negotiate.NTLMSSP_NEGOTIATE_ALWAYS_SIGN |
                                        Negotiate.NTLMSSP_NEGOTIATE_NTLM |
                                        Negotiate.NTLMSSP_NEGOTIATE_SEAL |
                                        Negotiate.NTLMSSP_NEGOTIATE_SIGN |
                                        Negotiate.NTLMSSP_REQUEST_TARGET |
                                        Negotiate.NTLMSSP_NEGOTIATE_UNICODE)
        return message
    
    def getAuthenticateMessage(self, s):
        """
        @summary: Client last handshake message
        @param s: {Stream} challenge message stream
        @return: {(AuthenticateMessage, NTLMv2SecurityInterface)} Last handshake message and security interface use to encrypt
        @see: https://msdn.microsoft.com/en-us/library/cc236676.aspx
        """
        challenge = ChallengeMessage()
        s.readType(challenge)
        
        ServerChallenge = challenge.ServerChallenge.value
        ClientChallenge = random(64)
        Timestamp = CurrentFileTimes()
        ServerName = challenge.getTargetInfo()
        
        NtChallengeResponse, LmChallengeResponse, SessionBaseKey = ComputeResponsev2(self._ResponseKeyNT, self._ResponseKeyLM, ServerChallenge, ClientChallenge, Timestamp, ServerName)
        KeyExchangeKey = KXKEYv2(SessionBaseKey, LmChallengeResponse, ServerChallenge)
        ExportedSessionKey = random(128)
        EncryptedRandomSessionKey = RC4K(KeyExchangeKey, ExportedSessionKey)
        
        domain, user = self._domain, self._user
        if challenge.NegotiateFlags.value & Negotiate.NTLMSSP_NEGOTIATE_UNICODE:
            domain, user = UNICODE(domain), UNICODE(user)
        message = createAuthenticationMessage(domain, user, NtChallengeResponse, LmChallengeResponse, EncryptedRandomSessionKey)
        
        ClientSigningKey = SIGNKEY(ExportedSessionKey, True)
        ServerSigningKey = SIGNKEY(ExportedSessionKey, False)
        ClientSealingKey = SEALKEY(ExportedSessionKey, True)
        ServerSealingKey = SEALKEY(ExportedSessionKey, False)
        
        interface = NTLMv2SecurityInterface(rc4.RC4Key(ClientSealingKey), rc4.RC4Key(ServerSealingKey), ClientSigningKey, ServerSigningKey)
        
        return message, interface
        

class NTLMv2SecurityInterface(sspi.IGenericSecurityService):
    """
    @summary: Generic Security Service for NTLM session
    """
    def __init__(self, encryptHandle, decryptHandle, signingKey, verifyKey):
        """
        @param encryptHandle: {rc4.RC4Key} rc4 keystream for encrypt phase
        @param decryptHandle: {rc4.RC4Key} rc4 keystream for decrypt phase
        @param signingKey: {str} signingKey
        @param verifyKey: {str} verifyKey
        """
        self._encryptHandle = encryptHandle
        self._decryptHandle = decryptHandle
        self._signingKey = signingKey
        self._verifyKey = verifyKey
        self._seqNum = 0
        
    def GSS_WrapEx(self, data):
        """
        @summary: Encrypt function for NTLMv2 security service
        @param data: data to encrypt
        @return: {str} encrypted data
        """
        encryptedData = rc4.crypt(self._encryptHandle, data)
        signature = MAC(self._encryptHandle, self._signingKey, self._seqNum, data)
        self._seqNum += 1
        s = Stream()
        s.writeType(signature)
        return s.getvalue() + encryptedData

pubKeyHex = [
0x30, 0x81, 0x89, 0x02, 0x81, 0x81, 0x00, 0x9E, 
0x95, 0xB5, 0x41, 0x03, 0xC5, 0x33, 0xEA, 0x29, 
0x65, 0x2B, 0x65, 0xEF, 0x30, 0x71, 0xDD, 0x73, 
0xBB, 0x30, 0x3B, 0xEC, 0xCA, 0x72, 0xCF, 0xBD, 
0xE0, 0xF8, 0x21, 0xFF, 0xA6, 0x97, 0x76, 0xA1, 
0x08, 0xB5, 0xD2, 0xC6, 0x95, 0x81, 0xD2, 0xBA, 
0x71, 0x10, 0x4A, 0xAC, 0x25, 0x34, 0x37, 0xA0, 
0xC3, 0x57, 0xF0, 0xEA, 0x1F, 0x8C, 0x84, 0xEB, 
0x7B, 0xE6, 0x6C, 0x50, 0x26, 0x1F, 0xB7, 0x41, 
0x0A, 0x58, 0xD3, 0x80, 0x87, 0x3D, 0x0B, 0x41, 
0xD9, 0xBC, 0x54, 0x3A, 0x0F, 0x77, 0x14, 0x79, 
0xF5, 0xB9, 0xA4, 0x38, 0xEB, 0x13, 0x08, 0x35, 
0xAE, 0xBF, 0xB3, 0x17, 0x5A, 0xE2, 0x58, 0x89, 
0x39, 0xC4, 0x22, 0x7F, 0x16, 0x57, 0x90, 0x08, 
0xAF, 0x91, 0x3B, 0x95, 0xC8, 0x53, 0xD0, 0xC0, 
0x8E, 0x19, 0x8A, 0xF3, 0x10, 0xBC, 0xC8, 0xC7, 
0x42, 0xFB, 0x12, 0xDE, 0x2D, 0x5E, 0x83, 0x02, 
0x03, 0x01, 0x00, 0x01 ]

peer0_0 = [
0x30, 0x2f, 0xa0, 0x03, 0x02, 0x01, 0x02, 0xa1, 
0x28, 0x30, 0x26, 0x30, 0x24, 0xa0, 0x22, 0x04, 
0x20, 0x4e, 0x54, 0x4c, 0x4d, 0x53, 0x53, 0x50, 
0x00, 0x01, 0x00, 0x00, 0x00, 0x35, 0x82, 0x08, 
0x60, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
0x00 ]
peer1_0 = [
0x30, 0x82, 0x01, 0x09, 0xa0, 0x03, 0x02, 0x01, 
0x02, 0xa1, 0x82, 0x01, 0x00, 0x30, 0x81, 0xfd, 
0x30, 0x81, 0xfa, 0xa0, 0x81, 0xf7, 0x04, 0x81, 
0xf4, 0x4e, 0x54, 0x4c, 0x4d, 0x53, 0x53, 0x50, 
0x00, 0x02, 0x00, 0x00, 0x00, 0x0e, 0x00, 0x0e, 
0x00, 0x38, 0x00, 0x00, 0x00, 0x35, 0x82, 0x89, 
0x62, 0x0a, 0xee, 0xd7, 0xc3, 0xeb, 0x8e, 0x34, 
0x6a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
0x00, 0xae, 0x00, 0xae, 0x00, 0x46, 0x00, 0x00, 
0x00, 0x06, 0x01, 0xb1, 0x1d, 0x00, 0x00, 0x00, 
0x0f, 0x53, 0x00, 0x49, 0x00, 0x52, 0x00, 0x41, 
0x00, 0x44, 0x00, 0x45, 0x00, 0x4c, 0x00, 0x02, 
0x00, 0x0e, 0x00, 0x53, 0x00, 0x49, 0x00, 0x52, 
0x00, 0x41, 0x00, 0x44, 0x00, 0x45, 0x00, 0x4c, 
0x00, 0x01, 0x00, 0x16, 0x00, 0x57, 0x00, 0x41, 
0x00, 0x56, 0x00, 0x2d, 0x00, 0x47, 0x00, 0x4c, 
0x00, 0x57, 0x00, 0x2d, 0x00, 0x30, 0x00, 0x30, 
0x00, 0x39, 0x00, 0x04, 0x00, 0x1a, 0x00, 0x53, 
0x00, 0x69, 0x00, 0x72, 0x00, 0x61, 0x00, 0x64, 
0x00, 0x65, 0x00, 0x6c, 0x00, 0x2e, 0x00, 0x6c, 
0x00, 0x6f, 0x00, 0x63, 0x00, 0x61, 0x00, 0x6c, 
0x00, 0x03, 0x00, 0x32, 0x00, 0x77, 0x00, 0x61, 
0x00, 0x76, 0x00, 0x2d, 0x00, 0x67, 0x00, 0x6c, 
0x00, 0x77, 0x00, 0x2d, 0x00, 0x30, 0x00, 0x30, 
0x00, 0x39, 0x00, 0x2e, 0x00, 0x53, 0x00, 0x69, 
0x00, 0x72, 0x00, 0x61, 0x00, 0x64, 0x00, 0x65, 
0x00, 0x6c, 0x00, 0x2e, 0x00, 0x6c, 0x00, 0x6f, 
0x00, 0x63, 0x00, 0x61, 0x00, 0x6c, 0x00, 0x05, 
0x00, 0x1a, 0x00, 0x53, 0x00, 0x69, 0x00, 0x72, 
0x00, 0x61, 0x00, 0x64, 0x00, 0x65, 0x00, 0x6c, 
0x00, 0x2e, 0x00, 0x6c, 0x00, 0x6f, 0x00, 0x63, 
0x00, 0x61, 0x00, 0x6c, 0x00, 0x07, 0x00, 0x08, 
0x00, 0xe5, 0x40, 0x3c, 0xa6, 0x68, 0x57, 0xd0, 
0x01, 0x00, 0x00, 0x00, 0x00 ]
peer0_1 = [
0x30, 0x82, 0x02, 0x21, 0xa0, 0x03, 0x02, 0x01, 
0x02, 0xa1, 0x82, 0x01, 0x76, 0x30, 0x82, 0x01, 
0x72, 0x30, 0x82, 0x01, 0x6e, 0xa0, 0x82, 0x01, 
0x6a, 0x04, 0x82, 0x01, 0x66, 0x4e, 0x54, 0x4c, 
0x4d, 0x53, 0x53, 0x50, 0x00, 0x03, 0x00, 0x00, 
0x00, 0x18, 0x00, 0x18, 0x00, 0x64, 0x00, 0x00, 
0x00, 0xda, 0x00, 0xda, 0x00, 0x7c, 0x00, 0x00, 
0x00, 0x0e, 0x00, 0x0e, 0x00, 0x40, 0x00, 0x00, 
0x00, 0x16, 0x00, 0x16, 0x00, 0x4e, 0x00, 0x00, 
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
0x00, 0x10, 0x00, 0x10, 0x00, 0x56, 0x01, 0x00, 
0x00, 0x00, 0x00, 0x00, 0x00, 0x73, 0x00, 0x69, 
0x00, 0x72, 0x00, 0x61, 0x00, 0x64, 0x00, 0x65, 
0x00, 0x6c, 0x00, 0x73, 0x00, 0x70, 0x00, 0x65, 
0x00, 0x79, 0x00, 0x72, 0x00, 0x65, 0x00, 0x66, 
0x00, 0x69, 0x00, 0x74, 0x00, 0x74, 0x00, 0x65, 
0x00, 0x8a, 0x01, 0x34, 0xd8, 0x57, 0x6e, 0x14, 
0x2b, 0xda, 0xc6, 0x91, 0x02, 0x49, 0xbb, 0xc4, 
0x00, 0x19, 0x6c, 0x60, 0x26, 0x16, 0xdb, 0x37, 
0x8f, 0x98, 0xe1, 0x04, 0xf8, 0x36, 0x6a, 0x96, 
0xa2, 0xa1, 0x9a, 0xf9, 0x5f, 0x1f, 0x04, 0x63, 
0x69, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 
0x00, 0x38, 0x8d, 0x10, 0x08, 0x71, 0x57, 0xd0, 
0x01, 0x19, 0x6c, 0x60, 0x26, 0x16, 0xdb, 0x37, 
0x8f, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x0e, 
0x00, 0x53, 0x00, 0x49, 0x00, 0x52, 0x00, 0x41, 
0x00, 0x44, 0x00, 0x45, 0x00, 0x4c, 0x00, 0x01, 
0x00, 0x16, 0x00, 0x57, 0x00, 0x41, 0x00, 0x56, 
0x00, 0x2d, 0x00, 0x47, 0x00, 0x4c, 0x00, 0x57, 
0x00, 0x2d, 0x00, 0x30, 0x00, 0x30, 0x00, 0x39, 
0x00, 0x04, 0x00, 0x1a, 0x00, 0x53, 0x00, 0x69, 
0x00, 0x72, 0x00, 0x61, 0x00, 0x64, 0x00, 0x65, 
0x00, 0x6c, 0x00, 0x2e, 0x00, 0x6c, 0x00, 0x6f, 
0x00, 0x63, 0x00, 0x61, 0x00, 0x6c, 0x00, 0x03, 
0x00, 0x32, 0x00, 0x77, 0x00, 0x61, 0x00, 0x76, 
0x00, 0x2d, 0x00, 0x67, 0x00, 0x6c, 0x00, 0x77, 
0x00, 0x2d, 0x00, 0x30, 0x00, 0x30, 0x00, 0x39, 
0x00, 0x2e, 0x00, 0x53, 0x00, 0x69, 0x00, 0x72, 
0x00, 0x61, 0x00, 0x64, 0x00, 0x65, 0x00, 0x6c, 
0x00, 0x2e, 0x00, 0x6c, 0x00, 0x6f, 0x00, 0x63, 
0x00, 0x61, 0x00, 0x6c, 0x00, 0x05, 0x00, 0x1a, 
0x00, 0x53, 0x00, 0x69, 0x00, 0x72, 0x00, 0x61, 
0x00, 0x64, 0x00, 0x65, 0x00, 0x6c, 0x00, 0x2e, 
0x00, 0x6c, 0x00, 0x6f, 0x00, 0x63, 0x00, 0x61, 
0x00, 0x6c, 0x00, 0x07, 0x00, 0x08, 0x00, 0xe5, 
0x40, 0x3c, 0xa6, 0x68, 0x57, 0xd0, 0x01, 0x00, 
0x00, 0x00, 0x00, 0x59, 0x49, 0x84, 0x63, 0xf2, 
0x84, 0x53, 0x18, 0xea, 0xa4, 0xc3, 0xb6, 0x97, 
0x0d, 0x3e, 0x38, 0xa3, 0x81, 0x9f, 0x04, 0x81, 
0x9c, 0x01, 0x00, 0x00, 0x00, 0xc9, 0x56, 0x22, 
0x84, 0x7d, 0xba, 0xa2, 0xe6, 0x00, 0x00, 0x00, 
0x00, 0x1c, 0x6d, 0x39, 0xe1, 0x5a, 0x31, 0x5d, 
0xf5, 0x01, 0xa6, 0xea, 0x4b, 0xaf, 0x83, 0x13, 
0xdc, 0x8a, 0x45, 0xb3, 0x76, 0xc6, 0x3d, 0xbf, 
0x73, 0x4c, 0x93, 0xe6, 0x75, 0x8b, 0x42, 0x21, 
0xea, 0xe6, 0x0c, 0xfa, 0x3c, 0xd0, 0x7c, 0x8d, 
0xd6, 0x2a, 0x97, 0x7a, 0x49, 0xb5, 0x7d, 0xeb, 
0xc2, 0x94, 0xc0, 0x84, 0xb4, 0xef, 0x7f, 0x1e, 
0xa3, 0xa3, 0x3f, 0x61, 0x7c, 0x1c, 0xd9, 0x82, 
0xc6, 0x0b, 0x6c, 0x85, 0x15, 0xb0, 0x47, 0x25, 
0xe9, 0x0a, 0x88, 0x58, 0x3c, 0x6d, 0x8e, 0x60, 
0x2a, 0xbc, 0x04, 0x57, 0x7f, 0x5b, 0x03, 0x7c, 
0x7a, 0x8f, 0x1b, 0x7b, 0xe3, 0x67, 0xb6, 0x02, 
0xa4, 0xc0, 0xdd, 0x9e, 0x97, 0x4c, 0xd8, 0x86, 
0x5c, 0x9a, 0x45, 0x0d, 0x85, 0x4b, 0x46, 0x87, 
0xde, 0xcf, 0x31, 0x72, 0xe3, 0xd7, 0x5d, 0x0b, 
0x67, 0x1b, 0xa1, 0xde, 0x24, 0x87, 0xdf, 0xd9, 
0xb2, 0x18, 0xfd, 0x5a, 0x29, 0xbb, 0x35, 0xe0, 
0x3d, 0x9f, 0x85, 0xf7, 0x36 ]

if __name__ == "__main__":
    import cssp, hexdump
    negotiate_data_request = cssp.decodeDERTRequest(Stream("".join([chr(i) for i in peer0_0])))
    challenge_data_request = cssp.decodeDERTRequest(Stream("".join([chr(i) for i in peer1_0])))
    authenticate_data_request = cssp.decodeDERTRequest(Stream("".join([chr(i) for i in peer0_1])))
    
    negotiate_data = cssp.getNegoTokens(negotiate_data_request)[0]
    challenge_data = cssp.getNegoTokens(challenge_data_request)[0]
    authenticate_data = cssp.getNegoTokens(authenticate_data_request)[0]
    
    negotiate = NegotiateMessage()
    negotiate_data.readType(negotiate)
    
    challenge = ChallengeMessage()
    challenge_data.readType(challenge)
    
    ServerChallenge = challenge.ServerChallenge.value
    ServerName = challenge.getTargetInfo()
    
    authenticate = AuthenticateMessage()
    authenticate_data.readType(authenticate)
    
    NtChallengeResponseTemp = authenticate.getNtChallengeResponse()
    NTProofStr = NtChallengeResponseTemp[:16]
    temp = NtChallengeResponseTemp[16:]
    Timestamp = temp[8:16]
    ClientChallenge = temp[16:24]
    EncryptedRandomSessionKey = authenticate.getEncryptedRandomSession()
    
    domain = "siradel"
    user = "speyrefitte"
    password = "spe+99@12"
    ResponseKeyNT = NTOWFv2(password, user, domain)
    ResponseKeyLM = LMOWFv2(password, user, domain)
        
    NtChallengeResponse, LmChallengeResponse, SessionBaseKey = ComputeResponsev2(ResponseKeyNT, ResponseKeyLM, ServerChallenge, ClientChallenge, Timestamp, ServerName)
    KeyExchangeKey = KXKEYv2(SessionBaseKey, LmChallengeResponse, ServerChallenge)
    ExportedSessionKey = RC4K(KeyExchangeKey, EncryptedRandomSessionKey)
    
    domain, user = domain, user
    if challenge.NegotiateFlags.value & Negotiate.NTLMSSP_NEGOTIATE_UNICODE:
        domain, user = UNICODE(domain), UNICODE(user)
    message = createAuthenticationMessage(domain, user, NtChallengeResponse, LmChallengeResponse, EncryptedRandomSessionKey)
    
    ClientSigningKey = SIGNKEY(ExportedSessionKey, True)
    ServerSigningKey = SIGNKEY(ExportedSessionKey, False)
    ClientSealingKey = SEALKEY(ExportedSessionKey, True)
    ServerSealingKey = SEALKEY(ExportedSessionKey, False)
    
    interface = NTLMv2SecurityInterface(rc4.RC4Key(ClientSealingKey), rc4.RC4Key(ServerSealingKey), ClientSigningKey, ServerSigningKey)
    
    EncryptedPubKeySrc = cssp.getPubKeyAuth(authenticate_data_request)
    EncryptedPubKeyDst = interface.GSS_WrapEx("".join([chr(i) for i in pubKeyHex]))
    
    print "EncryptedPubKeySrc"
    hexdump.hexdump(EncryptedPubKeySrc)
    print "EncryptedPubKeyDst"
    hexdump.hexdump(EncryptedPubKeyDst)