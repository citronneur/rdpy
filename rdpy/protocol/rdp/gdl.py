'''
@author: sylvain
'''

from rdpy.protocol.network.layer import LayerAutomata
from rdpy.protocol.network.type import CompositeType, UniString, UInt16Le, UInt16Be, UInt32Le, sizeof
from rdpy.utils.const import ConstAttributes, TypeAttributes
from rdpy.protocol.network.error import InvalidExpectedDataException

import gcc

@ConstAttributes
@TypeAttributes(UInt16Le)
class SecurityFlag(object):
    '''
    microsoft security flags
    '''
    SEC_INFO_PKT = 0x0040
    SEC_LICENSE_PKT = 0x0080

@ConstAttributes
@TypeAttributes(UInt32Le)
class InfoFlag(object):
    '''
    client capabilities informations
    '''
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
    '''
    network performances flag
    '''
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
    '''
    client informations
    contains credentials (very important packet)
    '''
    def __init__(self, initForWrite, extendedInfoConditional):
        CompositeType.__init__(self)
        #code page
        self.codePage = UInt32Le()
        #support flag
        self.flag =         InfoFlag.INFO_MOUSE | InfoFlag.INFO_UNICODE | InfoFlag.INFO_LOGONERRORS | InfoFlag.INFO_LOGONNOTIFY | InfoFlag.INFO_ENABLEWINDOWSKEY | InfoFlag.INFO_DISABLECTRLALTDEL
        #length of domain unistring less 2 byte null terminate
        self.cbDomain =     UInt16Le(lambda:sizeof(self.domain) - 2)
        #length of username unistring less 2 byte null terminate
        self.cbUserName =   UInt16Le(lambda:sizeof(self.userName) - 2)
        #length of password unistring less 2 byte null terminate
        self.cbPassword =   UInt16Le(lambda:sizeof(self.password) - 2)
        #length of alternateshell unistring less 2 byte null terminate
        self.cbAlternateShell = UInt16Le(lambda:sizeof(self.alternateShell) - 2)
        #length of working directory unistring less 2 byte null terminate
        self.cbWorkingDir = UInt16Le(lambda:sizeof(self.workingDir) - 2)
        #to avoid recurcive loop init differ from reading and writing
        #microsoft domain
        self.domain =       UniString("" if initForWrite else lambda:"\x00" * self.cbDomain.value)
        #session username
        self.userName =     UniString("" if initForWrite else lambda:"\x00" * self.cbUserName.value)
        #associate password
        self.password =     UniString("" if initForWrite else lambda:"\x00" * self.cbPassword.value)
        #shell execute at start of session
        self.alternateShell = UniString("" if initForWrite else lambda:"\x00" * self.cbAlternateShell.value)
        #working directory for session
        self.workingDir =   UniString("" if initForWrite else lambda:"\x00" * self.cbWorkingDir.value)
        #more client informations
        self.extendedInfo = RDPExtendedInfo(initForWrite, conditional = extendedInfoConditional)
        
class RDPExtendedInfo(CompositeType):
    '''
    add more client informations
    use for performance flag!!!
    '''
    def __init__(self, initForWrite, conditional):
        CompositeType.__init__(self, conditional = conditional)
        #is an ip v4 or v6 adresse
        self.clientAddressFamily = AfInet.AF_INET
        #len of adress field
        self.cbClientAddress = UInt16Le(lambda:sizeof(self.clientAddress))
        #adress of client
        self.clientAddress = UniString("" if initForWrite else lambda:"\x00" * self.cbClientAddress.value)
        #len of client directory
        self.cbClientDir = UInt16Le(lambda:sizeof(self.clientDir))
        #self client directory
        self.clientDir = UniString("" if initForWrite else lambda:"\x00" * self.cbClientDir.value)
        #TODO make tiomezone
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
        self._info = RDPInfo(initForWrite = True, extendedInfoConditional = lambda:self._transport._serverSettings.core.rdpVersion == gcc.Version.RDP_VERSION_5_PLUS)
        
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
        self._transport.send(self._channelId, (SecurityFlag.SEC_INFO_PKT, UInt16Le(), self._info))
    
    def recvLicenceInfo(self, data):
        securityFlag = UInt16Le()
        securityFlagHi = UInt16Le()
        data.readType((securityFlag, securityFlagHi))
        
        if securityFlag & SecurityFlag.SEC_LICENSE_PKT != SecurityFlag.SEC_LICENSE_PKT:
            raise InvalidExpectedDataException("waiting license packet")