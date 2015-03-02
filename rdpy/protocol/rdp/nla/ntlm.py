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

import hashlib, hmac
import rdpy.security.pyDes as pyDes
from rdpy.security.rsa_wrapper import random
from rdpy.core.type import CompositeType, CallableValue, String, UInt8, UInt16Le, UInt24Le, UInt32Le, sizeof

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

class NegotiateMessage(CompositeType):
    """
    @summary: Message send from client to server to negotiate capability of NTLM Authentication
    @see: https://msdn.microsoft.com/en-us/library/cc236641.aspx
    """
    def __init__(self):
        CompositeType.__init__(self)
        self.Signature = String("NTLMSSP\x00", readLen = CallableValue(8), constant = True)
        self.MessageType = UInt32Le(0x00000001, constant = True)
        
        self.NegotiateFlags = UInt32Le(Negotiate.NTLMSSP_NEGOTIATE_KEY_EXCH |
                              Negotiate.NTLMSSP_NEGOTIATE_128 |
                              Negotiate.NTLMSSP_NEGOTIATE_56 |
                              Negotiate.NTLMSSP_NEGOTIATE_EXTENDED_SESSIONSECURITY |
                              Negotiate.NTLMSSP_NEGOTIATE_ALWAYS_SIGN |
                              Negotiate.NTLMSSP_NEGOTIATE_NTLM |
                              Negotiate.NTLMSSP_REQUEST_TARGET |
                              Negotiate.NTLMSSP_NEGOTIATE_TARGET_INFO |
                              Negotiate.NTLMSSP_NEGOTIATE_VERSION |
                              Negotiate.NTLMSSP_NEGOTIATE_UNICODE)
        
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
        if self.TargetNameLen.value == 0:
            return None
        offset = sizeof(self) - sizeof(self.Payload)
        start = self.TargetNameBufferOffset.value - offset
        end = start + self.TargetNameLen.value
        return self.Payload.value[start:end]
    
    def getTargetInfo(self):
        if self.TargetInfoLen.value == 0:
            return None
        offset = sizeof(self) - sizeof(self.Payload)
        start = self.TargetInfoBufferOffset.value - offset
        end = start + self.TargetInfoLen.value - 4
        return self.Payload.value[start:end]
        
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
        if self.UserNameLen.value == 0:
            return None
        offset = sizeof(self) - sizeof(self.Payload)
        start = self.UserNameBufferOffset.value - offset
        end = start + self.UserNameLen.value
        return self.Payload.value[start:end]
    
    def getDomainName(self):
        if self.DomainNameLen.value == 0:
            return None
        offset = sizeof(self) - sizeof(self.Payload)
        start = self.DomainNameBufferOffset.value - offset
        end = start + self.DomainNameLen.value
        return self.Payload.value[start:end]

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
   
def NTOWFv1(Passwd, User, UserDom):
    """
    @see: https://msdn.microsoft.com/en-us/library/cc236699.aspx
    """
    return MD4(UNICODE(Passwd))

def LMOWFv1(Passwd, User, UserDom):
    """
    @see: https://msdn.microsoft.com/en-us/library/cc236699.aspx
    """
    password = (Passwd.upper() + "\x00" * 14)[:14]
    return DES(password[:7], "KGS!@#$%") + DES(password[7:], "KGS!@#$%")

def NTLMv1Anthentication(negFlag, domain, user, password, serverChallenge, serverName):
    """
    @summary: Not tested yet
    @param negFlag: {int} use another non secure way
    @param domain: {str} microsoft domain
    @param user: {str} username
    @param password: {str} password
    @param serverChallenge: {str[8]} server challenge
    """
    ResponseKeyNT = NTOWFv1(password, user, domain)
    ResponseKeyLM = LMOWFv1(password, user, domain)
    
    if negFlag & Negotiate.NTLMSSP_NEGOTIATE_EXTENDED_SESSIONSECURITY:
        ClientChallenge = random(64)
        NtChallengeResponse = DESL(ResponseKeyNT, MD5(serverChallenge + ClientChallenge))
        LmChallengeResponse = ClientChallenge + Z(16)
    else:
        NtChallengeResponse = DESL(ResponseKeyNT, serverChallenge)
        LmChallengeResponse = DESL(ResponseKeyLM, serverChallenge)
        
    SessionBaseKey = MD4(ResponseKeyNT)
    
    return NtChallengeResponse, LmChallengeResponse, SessionBaseKey

def HMAC_MD5(key, data):
    return hmac.new(key, data, hashlib.md5).digest()

def NTOWFv2(Passwd, User, UserDom):
    return HMAC_MD5(MD4(UNICODE(Passwd)), UNICODE(User.upper() + UserDom))

def LMOWFv2(Passwd, User, UserDom):
    return NTOWFv2(Passwd, User, UserDom)

def NTLMv2Authenticate(negFlag, domain, user, password, serverChallenge, serverName):
    """
    @summary: process NTLMv2 Authenticate hash
    @see: https://msdn.microsoft.com/en-us/library/cc236700.aspx
    """
    ResponseKeyNT = NTOWFv2(password, user, domain)
    ResponseKeyLM = LMOWFv2(password, user, domain)
    
    Responserversion = "\0x01"
    HiResponserversion = "0x01"
    Time = "\x00" * 8
    ClientChallenge = random(64)

    temp = Responserversion + HiResponserversion + Z(6) + Time + ClientChallenge + Z(4) + serverName + Z(4)
    NTProofStr = HMAC_MD5(ResponseKeyNT, serverChallenge + temp)
    NtChallengeResponse = NTProofStr + temp
    LmChallengeResponse = HMAC_MD5(ResponseKeyLM, serverChallenge + ClientChallenge) + ClientChallenge
    
    SessionBaseKey = HMAC_MD5(ResponseKeyNT, NTProofStr)
    
    return NtChallengeResponse, LmChallengeResponse, SessionBaseKey

def createAuthenticationMessage(method, challengeResponse, domain, user, password):
    #extract target info
    NtChallengeResponse, LmChallengeResponse, SessionBaseKey = method(challengeResponse.NegotiateFlags.value, 
                                                                      domain, user, password, 
                                                                      challengeResponse.ServerChallenge.value,
                                                                      challengeResponse.getTargetInfo())
    
    if challengeResponse.NegotiateFlags.value & Negotiate.NTLMSSP_NEGOTIATE_UNICODE:
        domain, user = UNICODE(domain), UNICODE(user)
    
    message = AuthenticateMessage()
    #fill message
    offset = sizeof(message)
    
    message.NegotiateFlags.value = challengeResponse.NegotiateFlags.value
    message.NegotiateFlags.value &= ~Negotiate.NTLMSSP_NEGOTIATE_VERSION
    
    message.LmChallengeResponseLen.value = len(LmChallengeResponse)
    message.LmChallengeResponseBufferOffset.value = offset
    message.Payload.value += LmChallengeResponse
    offset += len(LmChallengeResponse)
    
    message.NtChallengeResponseLen.value = len(NtChallengeResponse)
    message.NtChallengeResponseBufferOffset.value = offset
    message.Payload.value += NtChallengeResponse
    offset += len(NtChallengeResponse)
    
    message.DomainNameLen.value = len(domain)
    message.DomainNameBufferOffset.value = offset
    message.Payload.value += domain
    offset += len(domain)
    
    message.UserNameLen.value = len(user)
    message.UserNameBufferOffset.value = offset
    message.Payload.value += user
    offset += len(user)
    
    message.EncryptedRandomSessionLen.value = len(SessionBaseKey)
    message.EncryptedRandomSessionBufferOffset.value = offset
    message.Payload.value += SessionBaseKey
    offset += len(SessionBaseKey)
    
    return message