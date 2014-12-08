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
Some use full methods for security in RDP
"""

import sha, md5, rsa, gcc, rc4
from rdpy.network.type import CompositeType, Stream, UInt32Le, String, sizeof
from rdpy.network.layer import LayerAutomata, IStreamSender

class SecurityFlag(object):
    """
    @summary: Microsoft security flags
    @see: http://msdn.microsoft.com/en-us/library/cc240579.aspx
    """
    SEC_EXCHANGE_PKT = 0x0001
    SEC_TRANSPORT_REQ = 0x0002
    RDP_SEC_TRANSPORT_RSP = 0x0004
    SEC_ENCRYPT = 0x0008
    SEC_RESET_SEQNO = 0x0010
    SEC_IGNORE_SEQNO = 0x0020
    SEC_INFO_PKT = 0x0040
    SEC_LICENSE_PKT = 0x0080
    SEC_LICENSE_ENCRYPT_CS = 0x0200
    SEC_LICENSE_ENCRYPT_SC = 0x0200
    SEC_REDIRECTION_PKT = 0x0400
    SEC_SECURE_CHECKSUM = 0x0800
    SEC_AUTODETECT_REQ = 0x1000
    SEC_AUTODETECT_RSP = 0x2000
    SEC_HEARTBEAT = 0x4000
    SEC_FLAGSHI_VALID = 0x8000

def saltedHash(inputData, salt, salt1, salt2):
    """
    @summary: Generate particular signature from combination of sha1 and md5
    @see: http://msdn.microsoft.com/en-us/library/cc241992.aspx
    @param inputData: strange input (see doc)
    @param salt: salt for context call
    @param salt1: another salt (ex : client random)
    @param salt2: another another salt (ex: server random)
    @return : MD5(Salt + SHA1(Input + Salt + Salt1 + Salt2))
    """
    sha1Digest = sha.new()
    md5Digest = md5.new()
    
    sha1Digest.update(inputData)
    sha1Digest.update(salt[:48])
    sha1Digest.update(salt1)
    sha1Digest.update(salt2)
    sha1Sig = sha1Digest.digest()
    
    md5Digest.update(salt[:48])
    md5Digest.update(sha1Sig)
    
    return md5Digest.digest()

def finalHash(key, random1, random2):
    """
    @summary: MD5(in0[:16] + in1[:32] + in2[:32])
    @param key: in 16
    @param random1: in 32
    @param random2: in 32
    @return MD5(in0[:16] + in1[:32] + in2[:32])
    """
    md5Digest = md5.new()
    md5Digest.update(key)
    md5Digest.update(random1)
    md5Digest.update(random2)
    return md5Digest.digest()

def generateMicrosoftKeyABBCCC(secret, random1, random2):
    """
    @summary: Generate master secret
    @param secret: secret
    @param clientRandom : client random
    @param serverRandom : server random
    """
    return saltedHash("A", secret, random1, random2) + saltedHash("BB", secret, random1, random2) + saltedHash("CCC", secret, random1, random2)

def generateMicrosoftKeyXYYZZZ(secret, random1, random2):
    """
    @summary: Generate master secret
    @param secret: secret
    @param clientRandom : client random
    @param serverRandom : server random
    """
    return saltedHash("X", secret, random1, random2) + saltedHash("YY", secret, random1, random2) + saltedHash("ZZZ", secret, random1, random2)


def macData(macSaltKey, data):
    """
    @see: http://msdn.microsoft.com/en-us/library/cc241995.aspx
    """
    sha1Digest = sha.new()
    md5Digest = md5.new()
    
    #encode length
    s = Stream()
    s.writeType(UInt32Le(len(data)))
    
    sha1Digest.update(macSaltKey)
    sha1Digest.update("\x36" * 40)
    sha1Digest.update(s.getvalue())
    sha1Digest.update(data)
    
    sha1Sig = sha1Digest.digest()
    
    md5Digest.update(macSaltKey)
    md5Digest.update("\x5c" * 48)
    md5Digest.update(sha1Sig)
    
    return md5Digest.digest()

def bin2bn(b):
    """
    @summary: convert binary string to bignum
    @param b: binary string
    @return bignum
    """
    l = 0L
    for ch in b:
        l = (l<<8) | ord(ch)
    return l

def bn2bin(b):
    s = bytearray()
    i = (b.bit_length() + 7) / 8
    while i > 0:
        s.append((b >> ((i - 1) * 8)) & 0xff)
        i -= 1
    return s
    

class ClientSecurityExchangePDU(CompositeType):
    """
    @summary: contain client random for basic security
    @see: http://msdn.microsoft.com/en-us/library/cc240472.aspx
    """
    def __init__(self):
        CompositeType.__init__(self)
        self.length = UInt32Le(lambda:(sizeof(self) - 4))
        self.encryptedClientRandom = String(readLen = self.length)

class SecLayer(LayerAutomata, IStreamSender):
    """
    @summary: Basic RDP security manager
    This layer is Transparent as possible for upper layer 
    """
    def __init__(self, presentation):
        LayerAutomata.__init__(self, presentation)
        self._enableEncryption = False
        
    def connect(self):
        """
        @summary: send client random
        """
        self._enableEncryption = (self._transport.getGCCClientSettings.getBlock(gcc.MessageType.CS_CORE).serverSelectedProtocol == 0)
        if not self._enableEncryption:
            self._presentation.connect()
            return
        
        #generate client random
        self._clientRandom = rsa.randnum.read_random_bits(128)
        self._serverRandom = self._transport.getGCCServerSettings().getBlock(gcc.MessageType.SC_SECURITY).serverRandom.value
        self.generateKeys()
        
        #send client random encrypted with
        certificate = self._transport.getGCCServerSettings().getBlock(gcc.MessageType.SC_SECURITY).serverCertificate.certData
        serverPublicKey = rsa.PublicKey(bin2bn(certificate.PublicKeyBlob.modulus.value), certificate.PublicKeyBlob.pubExp.value)
        
        message = ClientSecurityExchangePDU()
        message.encryptedClientRandom.value = rsa.encrypt(self._clientRandom, serverPublicKey)
        self._transport.send(message)
        self._presentation.connect()
        
    def generateKeys(self):
        """
        @see: http://msdn.microsoft.com/en-us/library/cc240785.aspx
        """
        preMasterSecret = self._clientRandom[:24] + self._serverRandom[:24]
        masterSecret = generateMicrosoftKeyABBCCC(preMasterSecret, self._clientRandom, self._serverRandom)
        self._sessionKey = generateMicrosoftKeyXYYZZZ(masterSecret, self._clientRandom, self._serverRandom)
        
        self._macKey128 = self._sessionKey[:16]
        self._decrypt = finalHash(self._sessionKey[16:32], self._clientRandom, self._serverRandom)
        self._encrypt = finalHash(self._sessionKey[32:48], self._clientRandom, self._serverRandom)
        
    def recv(self, data):
        if not self._enableEncryption:
            self._presentation.recv(data)
            return
        
    def send(self, data):
        if not self._enableEncryption:
            self._presentation.recv(data)
            return
    
    def sendInfoPkt(self, data):
        self._transport.send()