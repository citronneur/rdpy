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
import rdpy.security.rc4 as rc4
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

def RC4K(key, plaintext):
    """
    @summary: Context free of rc4 encoding
    @param key: {str} key
    @param plaintext: {str} plaintext
    @return {str} encrypted text
    """
    return rc4.crypt(rc4.RC4Key(key), plaintext)

def KXKEY(SessionBaseKey, LmChallengeResponse, ServerChallenge):
    """
    @summary: Key eXchange Key
    @param SessionBaseKey: {str} computed by NTLMv1Anthentication or NTLMv2Authenticate function
    @param LmChallengeResponse : {str} computed by NTLMv1Anthentication or NTLMv2Authenticate function
    @param ServerChallenge : {str} Server chanllenge come from ChallengeMessage
    @see: https://msdn.microsoft.com/en-us/library/cc236710.aspx
    """
    return HMAC_MD5(SessionBaseKey, ServerChallenge + LmChallengeResponse[:8])
   
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

def NTLMv2Authenticate(negFlag, domain, user, password, serverChallenge, serverName, Time = "\x00" * 8, ClientChallenge = None):
    """
    @summary: process NTLMv2 Authenticate hash
    @see: https://msdn.microsoft.com/en-us/library/cc236700.aspx
    """
    ResponseKeyNT = NTOWFv2(password, user, domain)
    ResponseKeyLM = LMOWFv2(password, user, domain)
    
    Responserversion = "\x01"
    HiResponserversion = "\x01"
    #Time = "\x00" * 8
    if ClientChallenge is None:
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


cssp_1 = [
0x30, 0x2f, 0xa0, 0x03, 0x02, 0x01, 0x02, 0xa1, 
0x28, 0x30, 0x26, 0x30, 0x24, 0xa0, 0x22, 0x04, 
0x20, 0x4e, 0x54, 0x4c, 0x4d, 0x53, 0x53, 0x50, 
0x00, 0x01, 0x00, 0x00, 0x00, 0x35, 0x82, 0x08, 
0x60, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
0x00 ]
cssp_2 = [
0x30, 0x82, 0x01, 0x09, 0xa0, 0x03, 0x02, 0x01, 
0x02, 0xa1, 0x82, 0x01, 0x00, 0x30, 0x81, 0xfd, 
0x30, 0x81, 0xfa, 0xa0, 0x81, 0xf7, 0x04, 0x81, 
0xf4, 0x4e, 0x54, 0x4c, 0x4d, 0x53, 0x53, 0x50, 
0x00, 0x02, 0x00, 0x00, 0x00, 0x0e, 0x00, 0x0e, 
0x00, 0x38, 0x00, 0x00, 0x00, 0x35, 0x82, 0x89, 
0x62, 0x73, 0xc7, 0x43, 0xa9, 0xe7, 0xfc, 0xbb, 
0xfc, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
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
0x00, 0x56, 0x93, 0x34, 0x32, 0xc7, 0x55, 0xd0, 
0x01, 0x00, 0x00, 0x00, 0x00 ]
cssp_3 = [
0x30, 0x82, 0x02, 0x0f, 0xa0, 0x03, 0x02, 0x01, 
0x02, 0xa1, 0x82, 0x01, 0x62, 0x30, 0x82, 0x01, 
0x5e, 0x30, 0x82, 0x01, 0x5a, 0xa0, 0x82, 0x01, 
0x56, 0x04, 0x82, 0x01, 0x52, 0x4e, 0x54, 0x4c, 
0x4d, 0x53, 0x53, 0x50, 0x00, 0x03, 0x00, 0x00, 
0x00, 0x18, 0x00, 0x18, 0x00, 0x50, 0x00, 0x00, 
0x00, 0xda, 0x00, 0xda, 0x00, 0x68, 0x00, 0x00, 
0x00, 0x08, 0x00, 0x08, 0x00, 0x40, 0x00, 0x00, 
0x00, 0x08, 0x00, 0x08, 0x00, 0x48, 0x00, 0x00, 
0x00, 0x00, 0x00, 0x00, 0x00, 0x50, 0x00, 0x00, 
0x00, 0x10, 0x00, 0x10, 0x00, 0x42, 0x01, 0x00, 
0x00, 0x35, 0x82, 0x08, 0x60, 0x63, 0x00, 0x6f, 
0x00, 0x63, 0x00, 0x6f, 0x00, 0x74, 0x00, 0x6f, 
0x00, 0x74, 0x00, 0x6f, 0x00, 0x1a, 0x8a, 0xc2, 
0xbc, 0x64, 0xda, 0xc0, 0x28, 0x9b, 0xa8, 0x14, 
0x08, 0x51, 0x6d, 0xd6, 0xb8, 0x29, 0x09, 0xd2, 
0x99, 0x19, 0x33, 0x70, 0x9e, 0x51, 0xa0, 0x6e, 
0xc5, 0x39, 0x47, 0xf3, 0x9e, 0x96, 0x6a, 0xc3, 
0xfc, 0xb2, 0xeb, 0xc7, 0xe0, 0x01, 0x01, 0x00, 
0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x45, 0x08, 
0x32, 0xc7, 0x55, 0xd0, 0x01, 0x29, 0x09, 0xd2, 
0x99, 0x19, 0x33, 0x70, 0x9e, 0x00, 0x00, 0x00, 
0x00, 0x02, 0x00, 0x0e, 0x00, 0x53, 0x00, 0x49, 
0x00, 0x52, 0x00, 0x41, 0x00, 0x44, 0x00, 0x45, 
0x00, 0x4c, 0x00, 0x01, 0x00, 0x16, 0x00, 0x57, 
0x00, 0x41, 0x00, 0x56, 0x00, 0x2d, 0x00, 0x47, 
0x00, 0x4c, 0x00, 0x57, 0x00, 0x2d, 0x00, 0x30, 
0x00, 0x30, 0x00, 0x39, 0x00, 0x04, 0x00, 0x1a, 
0x00, 0x53, 0x00, 0x69, 0x00, 0x72, 0x00, 0x61, 
0x00, 0x64, 0x00, 0x65, 0x00, 0x6c, 0x00, 0x2e, 
0x00, 0x6c, 0x00, 0x6f, 0x00, 0x63, 0x00, 0x61, 
0x00, 0x6c, 0x00, 0x03, 0x00, 0x32, 0x00, 0x77, 
0x00, 0x61, 0x00, 0x76, 0x00, 0x2d, 0x00, 0x67, 
0x00, 0x6c, 0x00, 0x77, 0x00, 0x2d, 0x00, 0x30, 
0x00, 0x30, 0x00, 0x39, 0x00, 0x2e, 0x00, 0x53, 
0x00, 0x69, 0x00, 0x72, 0x00, 0x61, 0x00, 0x64, 
0x00, 0x65, 0x00, 0x6c, 0x00, 0x2e, 0x00, 0x6c, 
0x00, 0x6f, 0x00, 0x63, 0x00, 0x61, 0x00, 0x6c, 
0x00, 0x05, 0x00, 0x1a, 0x00, 0x53, 0x00, 0x69, 
0x00, 0x72, 0x00, 0x61, 0x00, 0x64, 0x00, 0x65, 
0x00, 0x6c, 0x00, 0x2e, 0x00, 0x6c, 0x00, 0x6f, 
0x00, 0x63, 0x00, 0x61, 0x00, 0x6c, 0x00, 0x07, 
0x00, 0x08, 0x00, 0x56, 0x93, 0x34, 0x32, 0xc7, 
0x55, 0xd0, 0x01, 0x00, 0x00, 0x00, 0x00, 0xbf, 
0xec, 0xf5, 0xf6, 0x69, 0x01, 0x3a, 0xef, 0x5b, 
0xd0, 0xab, 0xfe, 0x3f, 0xdf, 0x75, 0x30, 0xa3, 
0x82, 0x00, 0xa0, 0x04, 0x82, 0x00, 0x9c, 0x01, 
0x00, 0x00, 0x00, 0xc4, 0x0e, 0xcd, 0x96, 0x8f, 
0x67, 0xc0, 0xdd, 0x00, 0x00, 0x00, 0x00, 0xcf, 
0x88, 0xbd, 0x30, 0xe2, 0x53, 0x4a, 0x4b, 0x8d, 
0x49, 0xd4, 0xe9, 0xa3, 0x63, 0x1f, 0xe8, 0x19, 
0x59, 0xe6, 0x88, 0x96, 0xaa, 0x50, 0x35, 0x81, 
0x02, 0x9a, 0x91, 0x25, 0x8b, 0x1c, 0x0f, 0x8f, 
0xc6, 0x91, 0x44, 0x55, 0x5f, 0x4e, 0xd9, 0x1b, 
0xc3, 0xae, 0x94, 0xde, 0x09, 0xa8, 0xdd, 0x80, 
0x64, 0x52, 0x85, 0x4a, 0xf2, 0xd7, 0xc7, 0x11, 
0x29, 0x22, 0xbe, 0xe5, 0xad, 0x57, 0x6b, 0x4f, 
0xdc, 0xa1, 0xae, 0x00, 0x5b, 0xff, 0xe8, 0x6c, 
0xdb, 0x15, 0x84, 0x18, 0x94, 0x0e, 0xeb, 0xcd, 
0x9d, 0x41, 0xc3, 0x4e, 0xf6, 0xa6, 0xcf, 0x2c, 
0xf5, 0xc5, 0x9e, 0xa0, 0xd9, 0x80, 0x5f, 0xaa, 
0x22, 0x66, 0x61, 0x56, 0xde, 0x3e, 0xcb, 0x5f, 
0x7c, 0x64, 0xaf, 0xbf, 0xa7, 0x26, 0x83, 0xa8, 
0x5c, 0x88, 0xf3, 0xbe, 0x8a, 0xe6, 0xe6, 0x4c, 
0xf7, 0x95, 0xd0, 0xa8, 0xf0, 0x8c, 0x21, 0xf8, 
0x86, 0x77, 0x49, 0x29, 0xe3, 0xd3, 0xf8, 0x78, 
0x1f, 0x51, 0x91 ]

pubKey = "\x30\x81\x89\x02\x81\x81\x00\x9e\x95\xb5\x41\x03\xc5\x33\xea\x29\x65\x2b\x65\xef\x30\x71\xdd\x73\xbb\x30\x3b\xec\xca\x72\xcf\xbd\xe0\xf8\x21\xff\xa6\x97\x76\xa1\x08\xb5\xd2\xc6\x95\x81\xd2\xba\x71\x10\x4a\xac\x25\x34\x37\xa0\xc3\x57\xf0\xea\x1f\x8c\x84\xeb\x7b\xe6\x6c\x50\x26\x1f\xb7\x41\x0a\x58\xd3\x80\x87\x3d\x0b\x41\xd9\xbc\x54\x3a\x0f\x77\x14\x79\xf5\xb9\xa4\x38\xeb\x13\x08\x35\xae\xbf\xb3\x17\x5a\xe2\x58\x89\x39\xc4\x22\x7f\x16\x57\x90\x08\xaf\x91\x3b\x95\xc8\x53\xd0\xc0\x8e\x19\x8a\xf3\x10\xbc\xc8\xc7\x42\xfb\x12\xde\x2d\x5e\x83\x02\x03\x01\x00\x01"

if __name__ == "__main__":
    import cssp, hexdump
    from rdpy.core.type import Stream
    
    negotiate_data_request = cssp.decodeDERTRequest(Stream("".join([chr(i) for i in cssp_1])))
    challenge_data_request = cssp.decodeDERTRequest(Stream("".join([chr(i) for i in cssp_2])))
    authenticate_data_request = cssp.decodeDERTRequest(Stream("".join([chr(i) for i in cssp_3])))
    
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
    
    NtChallengeResponse = authenticate.getNtChallengeResponse()
    NTProofStr = NtChallengeResponse[:16]
    temp = NtChallengeResponse[16:]
    Time = temp[8:16]
    ClientChallenge = temp[16:24]
    ServerName2 = temp[28:-4]
    
    LmChallengeResponse = authenticate.getLmChallengeResponse()
    SessionBaseKey = authenticate.getEncryptedRandomSession()
    encryptedPubKey = cssp.getPubKeyAuth(authenticate_data_request)
    
    NtChallengeResponse2, LmChallengeResponse2, SessionBaseKey2 = NTLMv2Authenticate(None, "coco", "toto", "lolo", ServerChallenge, ServerName, Time, ClientChallenge)
    
    KeyExchangeKey = HMAC_MD5(SessionBaseKey2, ServerChallenge + LmChallengeResponse[:7])
    ExportedSessionKey = RC4K(KeyExchangeKey, SessionBaseKey)
    sealingKey = MD5(ExportedSessionKey + "session key to client-to-server sealing key magic constant")
    #sealingKey = MD5(sealingKey + "\x00" + "\x00" * 3)
    
    encryptedPubKey2 = RC4K(sealingKey, pubKey)
    
    hexdump.hexdump(encryptedPubKey)
    print "\n"
    hexdump.hexdump(encryptedPubKey2)
    print "-"*40
    print "NtChallengeResponse"
    print "\n"
    hexdump.hexdump(NtChallengeResponse)
    print "\n"
    hexdump.hexdump(NtChallengeResponse2)
    print "-"*40
     
    print "-"*40
    print "LmChallengeResponse"
    print "\n"
    hexdump.hexdump(LmChallengeResponse)
    print "\n"
    hexdump.hexdump(LmChallengeResponse2)
    print "-"*40
     
    print "-"*40
    print "SessionBaseKey"
    print "\n"
    hexdump.hexdump(SessionBaseKey)
    print "\n"
    hexdump.hexdump(SessionBaseKey2)
    print "-"*40