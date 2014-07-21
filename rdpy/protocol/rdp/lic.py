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
RDP extended license
@see: http://msdn.microsoft.com/en-us/library/cc241880.aspx
"""

from rdpy.network.type import CompositeType, UInt8, UInt16Le, UInt32Le, String, sizeof, FactoryType, ArrayType
from rdpy.base.error import InvalidExpectedDataException
import rdpy.base.log as log

class MessageType(object):
    """
    License packet message type
    """
    LICENSE_REQUEST = 0x01
    PLATFORM_CHALLENGE = 0x02
    NEW_LICENSE = 0x03
    UPGRADE_LICENSE = 0x04
    LICENSE_INFO = 0x12
    NEW_LICENSE_REQUEST = 0x13
    PLATFORM_CHALLENGE_RESPONSE = 0x15
    ERROR_ALERT = 0xFF
    
    
class ErrorCode(object):
    """
    License error message code
    @see: http://msdn.microsoft.com/en-us/library/cc240482.aspx
    """
    ERR_INVALID_SERVER_CERTIFICATE = 0x00000001
    ERR_NO_LICENSE = 0x00000002
    ERR_INVALID_SCOPE = 0x00000004
    ERR_NO_LICENSE_SERVER = 0x00000006
    STATUS_VALID_CLIENT = 0x00000007
    ERR_INVALID_CLIENT = 0x00000008
    ERR_INVALID_PRODUCTID = 0x0000000B
    ERR_INVALID_MESSAGE_LEN = 0x0000000C
    ERR_INVALID_MAC = 0x00000003
      
class StateTransition(object):
    """
    Automata state transition
    @see: http://msdn.microsoft.com/en-us/library/cc240482.aspx
    """
    ST_TOTAL_ABORT = 0x00000001
    ST_NO_TRANSITION = 0x00000002
    ST_RESET_PHASE_TO_START = 0x00000003
    ST_RESEND_LAST_MESSAGE = 0x00000004
    
class BinaryBlobType(object):
    """
    Binary blob data type
    @see: http://msdn.microsoft.com/en-us/library/cc240481.aspx
    """
    BB_DATA_BLOB = 0x0001
    BB_RANDOM_BLOB = 0x0002
    BB_CERTIFICATE_BLOB = 0x0003
    BB_ERROR_BLOB = 0x0004
    BB_ENCRYPTED_DATA_BLOB = 0x0009
    BB_KEY_EXCHG_ALG_BLOB = 0x000D
    BB_SCOPE_BLOB = 0x000E
    BB_CLIENT_USER_NAME_BLOB = 0x000F
    BB_CLIENT_MACHINE_NAME_BLOB = 0x0010

class Preambule(object):
    """
    Preambule version
    """
    PREAMBLE_VERSION_2_0 = 0x2
    PREAMBLE_VERSION_3_0 = 0x3
    
class LicenseBinaryBlob(CompositeType):
    """
    Blob use by license manager to exchange security data
    @see: http://msdn.microsoft.com/en-us/library/cc240481.aspx
    """
    def __init__(self, blobType = 0):
        CompositeType.__init__(self)
        self.wBlobType = UInt16Le(blobType, constant = True)
        self.wBlobLen = UInt16Le(lambda:sizeof(self.blobData))
        self.blobData = String(readLen = self.wBlobLen)

class LicensingErrorMessage(CompositeType):
    """
    License error message
    @see: http://msdn.microsoft.com/en-us/library/cc240482.aspx
    """
    _MESSAGE_TYPE_ = MessageType.ERROR_ALERT
    
    def __init__(self):
        CompositeType.__init__(self)
        self.dwErrorCode = UInt32Le()
        self.dwStateTransition = UInt32Le()
        self.blob = LicenseBinaryBlob(BinaryBlobType.BB_ERROR_BLOB)
        
class ProductInformation(CompositeType):
    """
    License server product information
    @see: http://msdn.microsoft.com/en-us/library/cc241915.aspx
    """
    def __init__(self):
        CompositeType.__init__(self)
        self.dwVersion = UInt32Le()
        self.cbCompanyName = UInt32Le(lambda:sizeof(self.pbCompanyName))
        #may contain "Microsoft Corporation" from server microsoft
        self.pbCompanyName = String(readLen = self.cbCompanyName)
        self.cbProductId = UInt32Le(lambda:sizeof(self.pbProductId))
        #may contain "A02" from microsoft license server
        self.pbProductId = String(readLen = self.cbProductId)


class Scope(CompositeType):
    """
    Use in license nego
    @see: http://msdn.microsoft.com/en-us/library/cc241917.aspx
    """
    def __init__(self):
        CompositeType.__init__(self)
        self.scope = LicenseBinaryBlob(BinaryBlobType.BB_SCOPE_BLOB)
              
class ScopeList(CompositeType):
    """
    Use in license nego
    @see: http://msdn.microsoft.com/en-us/library/cc241916.aspx
    """
    def __init__(self):
        CompositeType.__init__(self)
        self.scopeCount = UInt32Le(lambda:sizeof(self.scopeArray))
        self.scopeArray = ArrayType(Scope, readLen = self.scopeCount)
        
class ServerLicenseRequest(CompositeType):
    """
    Send by server to signal license request
    server -> client
    @see: http://msdn.microsoft.com/en-us/library/cc241914.aspx
    """
    _MESSAGE_TYPE_ = MessageType.LICENSE_REQUEST
    
    def __init__(self):
        CompositeType.__init__(self)
        self.serverRandom = String(readLen = UInt8(32))
        self.productInfo = ProductInformation()
        self.keyExchangeList = LicenseBinaryBlob(BinaryBlobType.BB_KEY_EXCHG_ALG_BLOB)
        self.serverCertificate = LicenseBinaryBlob(BinaryBlobType.BB_CERTIFICATE_BLOB)
        self.scopeList = ScopeList()
        
class ClientNewLicenseRequest(CompositeType):
    """
    Send by client to ask new license for client.
    RDPY doesn'support license reuse, need it in futur version
    @see: http://msdn.microsoft.com/en-us/library/cc241918.aspx
    """
    _MESSAGE_TYPE_ = MessageType.NEW_LICENSE_REQUEST
    
    def __init__(self):
        CompositeType.__init__(self)
        #RSA and must be only RSA
        self.preferredKeyExchangeAlg = UInt32Le(0x00000001, constant = True)
        #pure microsoft client ;-)
        #http://msdn.microsoft.com/en-us/library/1040af38-c733-4fb3-acd1-8db8cc979eda#id10
        self.platformId = UInt32Le(0x04000000 | 0x00010000)
        self.clientRandom = String("\x00" * 32)
        self.encryptedPreMasterSecret = LicenseBinaryBlob(BinaryBlobType.BB_RANDOM_BLOB)
        self.ClientUserName = LicenseBinaryBlob(BinaryBlobType.BB_CLIENT_USER_NAME_BLOB)
        self.ClientMachineName = LicenseBinaryBlob(BinaryBlobType.BB_CLIENT_MACHINE_NAME_BLOB)

class LicPacket(CompositeType):
    """
    A license packet
    """
    def __init__(self, message = None):
        CompositeType.__init__(self)
        #preambule
        self.bMsgtype = UInt8(lambda:self.licensingMessage.__class__._MESSAGE_TYPE_)
        self.flag = UInt8(Preambule.PREAMBLE_VERSION_3_0)
        self.wMsgSize = UInt16Le(lambda: sizeof(self))
        
        def LicensingMessageFactory():
            """
            factory for message nego
            Use in read mode
            """
            for c in [LicensingErrorMessage, ServerLicenseRequest, ClientNewLicenseRequest]:
                if self.bMsgtype.value == c._MESSAGE_TYPE_:
                    return c()
            log.debug("unknown license message : %s"%self.bMsgtype.value)
            return String()
        
        if message is None:
            message = FactoryType(LicensingMessageFactory)
        elif not "_MESSAGE_TYPE_" in message.__class__.__dict__:
            raise InvalidExpectedDataException("Try to send an invalid license message")
            
        self.licensingMessage = message

def createValidClientLicensingErrorMessage():
    """
    Create a licensing error message that accept client
    server automata message
    """
    message = LicensingErrorMessage()
    message.dwErrorCode.value = ErrorCode.STATUS_VALID_CLIENT
    message.dwStateTransition.value = StateTransition.ST_NO_TRANSITION
    return LicPacket(message = message)

def createNewLicenseRequest(serverLicenseRequest):
    """
    Create new license request in response to server license request
    @see: http://msdn.microsoft.com/en-us/library/cc241989.aspx
    @see: http://msdn.microsoft.com/en-us/library/cc241918.aspx
    @todo: need RDP license server
    """
    return LicPacket(message = ClientNewLicenseRequest())