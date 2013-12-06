'''
@author: sylvain
'''
from rdpy.protocol.network.type import CompositeType, UInt8, UInt16Le, sizeof
from rdpy.utils.const import ConstAttributes, TypeAttributes

@ConstAttributes
@TypeAttributes(UInt8)
class MessageType(object):
    LICENSE_REQUEST = 0x01
    PLATFORM_CHALLENGE = 0x02
    NEW_LICENSE = 0x03
    UPGRADE_LICENSE = 0x04
    LICENSE_INFO = 0x12
    NEW_LICENSE_REQUEST = 0x13
    PLATFORM_CHALLENGE_RESPONSE = 0x15
    ERROR_ALERT = 0xFF

class LicPacket(CompositeType):
    def __init__(self):
        #preambule
        self.bMsgtype = UInt8()
        self.flag = UInt8()
        self.wMsgSize = UInt16Le(lambda: sizeof(self))
        