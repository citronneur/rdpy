'''
@author sylvain
@summary gcc language
'''
from rdpy.utils.const import ConstAttributes
from rdpy.protocol.network.type import UInt32Le, UInt16Le, String, CompositeType


@ConstAttributes
class ServerToClientMessage(object):
    SC_CORE = UInt16Le(0x0C01)
    SC_SECURITY = UInt16Le(0x0C02)
    SC_NET = UInt16Le(0x0C03)

@ConstAttributes
class ClientToServerMessage(object):
    '''
    Client to Server message
    '''
    CS_CORE = UInt16Le(0xC001)
    CS_SECURITY = UInt16Le(0xC002)
    CS_NET = UInt16Le(0xC003)
    CS_CLUSTER = UInt16Le(0xC004)
    CS_MONITOR = UInt16Le(0xC005)

@ConstAttributes
class ColorDepth(object):
    '''
    depth color
    '''
    RNS_UD_COLOR_8BPP = UInt16Le(0xCA01)
    RNS_UD_COLOR_16BPP_555 = UInt16Le(0xCA02)
    RNS_UD_COLOR_16BPP_565 = UInt16Le(0xCA03)
    RNS_UD_COLOR_24BPP = UInt16Le(0xCA04)

RNS_UD_24BPP_SUPPORT =      0x0001
RNS_UD_16BPP_SUPPORT =      0x0002
RNS_UD_15BPP_SUPPORT =      0x0004
RNS_UD_32BPP_SUPPORT =      0x0008

RNS_UD_SAS_DEL =            0xAA03

RNS_UD_CS_SUPPORT_ERRINFO_PDU =       0x0001

@ConstAttributes
class Version(object):
    '''
    supported version of RDP
    '''
    RDP_VERSION_4 = UInt32Le(0x00080001)
    RDP_VERSION_5_PLUS = UInt32Le(0x00080004)


class ClientCoreSettings(CompositeType):
    '''
    class that represent core setting of client
    '''
    def __init__(self):
        CompositeType.__init__(self)
        self.rdpVersion = Version.RDP_VERSION_5_PLUS
        self.desktopWidth = UInt16Le(800)
        self.desktopHeight = UInt16Le(600)
        self.padding1 = (UInt16Le(), UInt16Le())
        self.kbdLayout = UInt32Le(0x409)
        self.clientBuild = UInt32Le(2100)
        self.clientName = "rdpy"
        self.padding2 = UInt16Le()
        self.keyboardType = UInt32Le(4)
        self.keyboardSubType = UInt32Le(0)
        self.keyboardFnKeys = UInt32Le(12)
        self.padding3 = String(" "*64)
        self.postBeta2ColorDepth = ColorDepth.RNS_UD_COLOR_24BPP
        self.padding4 = (UInt16Le(), UInt32Le())
        self.highColorDepth = UInt16Le(24)
        self.padding5 = (UInt16Le(), UInt16Le())
        self.padding3 = String(" "*64)
    
class ServerCoreSettings(CompositeType):
    '''
    server side core settings structure
    '''
    def __init__(self):
        CompositeType.__init__(self)
        self.rdpVersion = Version.RDP_VERSION_5_PLUS