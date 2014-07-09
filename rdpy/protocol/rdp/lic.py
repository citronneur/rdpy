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

from rdpy.network.type import CompositeType, UInt8, UInt16Le, UInt32Le, String, sizeof

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
    """
    ST_TOTAL_ABORT = 0x00000001
    ST_NO_TRANSITION = 0x00000002
    ST_RESET_PHASE_TO_START = 0x00000003
    ST_RESEND_LAST_MESSAGE = 0x00000004
    
class LicenceBinaryBlob(CompositeType):
    """
    Blob use by license manager to echange security data
    """
    def __init__(self):
        CompositeType.__init__(self)
        self.wBlobType = UInt16Le()
        self.wBlobLen = UInt16Le(lambda:sizeof(self.blobData))
        self.blobData = String(readLen = self.wBlobLen, conditional = lambda:self.wBlobLen.value > 0)

class LicensingErrorMessage(CompositeType):
    """
    License error message
    """
    def __init__(self, conditional = lambda:True):
        CompositeType.__init__(self, conditional = conditional)
        self.dwErrorCode = UInt32Le()
        self.dwStateTransition = UInt32Le()
        self.blob = LicenceBinaryBlob()

class LicPacket(CompositeType):
    """
    A license packet
    """
    def __init__(self):
        CompositeType.__init__(self)
        #preambule
        self.bMsgtype = UInt8()
        self.flag = UInt8()
        self.wMsgSize = UInt16Le(lambda: sizeof(self))
        self.errorMessage = LicensingErrorMessage(conditional = lambda:self.bMsgtype.value == MessageType.ERROR_ALERT)
        