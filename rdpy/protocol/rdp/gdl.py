'''
@author: sylvain
'''

from rdpy.protocol.network.layer import LayerAutomata
from rdpy.protocol.network.type import CompositeType, UniString, UInt16Le, UInt16Be, UInt32Le, sizeof
from rdpy.utils.const import ConstAttributes, TypeAttributes
from rdpy.protocol.network.error import InvalidExpectedDataException

@ConstAttributes
@TypeAttributes(UInt16Le)
class SecurityFlag(object):
    SEC_INFO_PKT = 0x0040
    SEC_LICENSE_PKT = 0x0080

@ConstAttributes
@TypeAttributes(UInt32Le)
class InfoFlag(object):
    INFO_MOUSE = 0x00000001
    INFO_DISABLECTRLALTDEL = 0x00000002
    INFO_AUTOLOGON = 0x00000008
    INFO_UNICODE = 0x00000010
    INFO_MAXIMIZESHELL = 0x00000020
    INFO_LOGONNOTIFY = 0x00000040
    INFO_COMPRESSION = 0x00000080
    INFO_ENABLEWINDOWSKEY = 0x00000100
    INFO_REMOTECONSOLEAUDIO = 0x00002000
    INFO_FORCE_ENCRYPTED_CS_PDU = 0x00004000
    INFO_RAIL = 0x00008000
    INFO_LOGONERRORS = 0x00010000
    INFO_MOUSE_HAS_WHEEL = 0x00020000
    INFO_PASSWORD_IS_SC_PIN = 0x00040000
    INFO_NOAUDIOPLAYBACK = 0x00080000
    INFO_USING_SAVED_CREDS = 0x00100000
    INFO_AUDIOCAPTURE = 0x00200000
    INFO_VIDEO_DISABLE = 0x00400000
    INFO_CompressionTypeMask = 0x00001E00

@ConstAttributes
@TypeAttributes(UInt32Le)
class PerfFlag(object):
    PERF_DISABLE_WALLPAPER = 0x00000001
    PERF_DISABLE_FULLWINDOWDRAG = 0x00000002
    PERF_DISABLE_MENUANIMATIONS = 0x00000004
    PERF_DISABLE_THEMING = 0x00000008
    PERF_DISABLE_CURSOR_SHADOW = 0x00000020
    PERF_DISABLE_CURSORSETTINGS = 0x00000040
    PERF_ENABLE_FONT_SMOOTHING = 0x00000080
    PERF_ENABLE_DESKTOP_COMPOSITION = 0x00000100

@ConstAttributes
@TypeAttributes(UInt16Le)
class AfInet(object):
    AF_INET = 0x00002
    AF_INET6 = 0x0017  

class RDPInfo(CompositeType):
    def __init__(self):
        CompositeType.__init__(self)
        self.codePage = UInt32Le()
        self.flag = InfoFlag.INFO_MOUSE | InfoFlag.INFO_UNICODE | InfoFlag.INFO_LOGONERRORS | InfoFlag.INFO_LOGONNOTIFY | InfoFlag.INFO_ENABLEWINDOWSKEY | InfoFlag.INFO_DISABLECTRLALTDEL
        self.cbDomain = UInt16Le(lambda:sizeof(self.domain) - 2)
        self.cbUserName = UInt16Le(lambda:sizeof(self.userName) - 2)
        self.cbPassword = UInt16Le(lambda:sizeof(self.password) - 2)
        self.cbAlternateShell = UInt16Le(lambda:sizeof(self.alternateShell) - 2)
        self.cbWorkingDir = UInt16Le(lambda:sizeof(self.workingDir) - 2)
        self.domain = UniString("coco")
        self.userName = UniString("lolo")
        self.password = UniString("toto")
        self.alternateShell = UniString()
        self.workingDir = UniString()
        
class RDPExtendedInfo(CompositeType):
    def __init__(self):
        CompositeType.__init__(self)
        self.clientAddressFamily = AfInet.AF_INET
        self.cbClientAddress = UInt16Le(lambda:sizeof(self.clientAddress))
        self.clientAddress = UniString("192.168.135.10")
        self.cbClientDir = UInt16Le(lambda:sizeof(self.clientDir))
        self.clientDir = UniString("c:\\")
        #self.performanceFlags = PerfFlag.PERF_DISABLE_WALLPAPER | PerfFlag.PERF_DISABLE_MENUANIMATIONS | PerfFlag.PERF_DISABLE_CURSOR_SHADOW

class GDL(LayerAutomata):
    '''
    Global Display Layer
    Global channel for mcs that handle session
    identification and user and graphic controls
    '''
    def __init__(self):
        '''
        Constructor
        '''
        LayerAutomata.__init__(self, None)
        #set by mcs layer channel init
        self._channelId = UInt16Be()
        #logon info send from client to server
        self._info = RDPInfo()
        self._extendedInfo = RDPExtendedInfo()
        
    def connect(self):
        '''
        connect event in client mode send logon info
        nextstate recv licence pdu
        '''
        self.sendInfoPkt()
        #next state is licence info PDU
        self.setNextState(self.recvLicenceInfo)
        
    def sendInfoPkt(self):
        '''
        send a logon info packet for RDP version 5 protocol
        '''
        #always send extended info because rdpy only accept rdp version 5 and more
        self._transport.send(self._channelId, (SecurityFlag.SEC_INFO_PKT, UInt16Le(), self._info, self._extendedInfo))
    
    def recvLicenceInfo(self, data):
        securityFlag = UInt16Le()
        securityFlagHi = UInt16Le()
        data.readType((securityFlag, securityFlagHi))
        
        if securityFlag & SecurityFlag.SEC_LICENSE_PKT != SecurityFlag.SEC_LICENSE_PKT:
            raise InvalidExpectedDataException("waiting license packet")