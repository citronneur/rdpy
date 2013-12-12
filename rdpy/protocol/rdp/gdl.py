'''
@author: sylvain
'''

from rdpy.protocol.network.layer import LayerAutomata
from rdpy.protocol.network.type import CompositeType, UniString, String, UInt8, UInt16Le, UInt16Be, UInt32Le, sizeof, ArrayType
from rdpy.utils.const import ConstAttributes, TypeAttributes
from rdpy.protocol.network.error import InvalidExpectedDataException

import gcc
import lic

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

@ConstAttributes
@TypeAttributes(UInt16Le)  
class PDUType(object):
    PDUTYPE_DEMANDACTIVEPDU = 0x1001
    PDUTYPE_CONFIRMACTIVEPDU = 0x3001
    PDUTYPE_DEACTIVATEALLPDU = 0x6001
    PDUTYPE_DATAPDU = 0x7001
    PDUTYPE_SERVER_REDIR_PKT = 0xA001
    
@ConstAttributes
@TypeAttributes(UInt16Le)     
class CapsType(object):
    '''
    different type of capabilities
    @see: http://msdn.microsoft.com/en-us/library/cc240486.aspx
    '''
    CAPSTYPE_GENERAL = 0x0001
    CAPSTYPE_BITMAP = 0x0002
    CAPSTYPE_ORDER = 0x0003
    CAPSTYPE_BITMAPCACHE = 0x0004
    CAPSTYPE_CONTROL = 0x0005
    CAPSTYPE_ACTIVATION = 0x0007
    CAPSTYPE_POINTER = 0x0008
    CAPSTYPE_SHARE = 0x0009
    CAPSTYPE_COLORCACHE = 0x000A
    CAPSTYPE_SOUND = 0x000C
    CAPSTYPE_INPUT = 0x000D
    CAPSTYPE_FONT = 0x000E
    CAPSTYPE_BRUSH = 0x000F
    CAPSTYPE_GLYPHCACHE = 0x0010
    CAPSTYPE_OFFSCREENCACHE = 0x0011
    CAPSTYPE_BITMAPCACHE_HOSTSUPPORT = 0x0012
    CAPSTYPE_BITMAPCACHE_REV2 = 0x0013
    CAPSTYPE_VIRTUALCHANNEL = 0x0014
    CAPSTYPE_DRAWNINEGRIDCACHE = 0x0015
    CAPSTYPE_DRAWGDIPLUS = 0x0016
    CAPSTYPE_RAIL = 0x0017
    CAPSTYPE_WINDOW = 0x0018
    CAPSETTYPE_COMPDESK = 0x0019
    CAPSETTYPE_MULTIFRAGMENTUPDATE = 0x001A
    CAPSETTYPE_LARGE_POINTER = 0x001B
    CAPSETTYPE_SURFACE_COMMANDS = 0x001C
    CAPSETTYPE_BITMAP_CODECS = 0x001D
    CAPSSETTYPE_FRAME_ACKNOWLEDGE = 0x001E
    
class RDPInfo(CompositeType):
    '''
    client informations
    contains credentials (very important packet)
    '''
    def __init__(self, extendedInfoConditional):
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
        #microsoft domain
        self.domain =       UniString(readLen = UInt16Le(lambda:self.cbDomain.value - 2))
        #session username
        self.userName =     UniString(readLen = UInt16Le(lambda:self.cbUserName.value - 2))
        #associate password
        self.password =     UniString(readLen = UInt16Le(lambda:self.cbPassword.value - 2))
        #shell execute at start of session
        self.alternateShell = UniString(readLen = UInt16Le(lambda:self.cbAlternateShell.value - 2))
        #working directory for session
        self.workingDir =   UniString(readLen = UInt16Le(lambda:self.cbWorkingDir.value - 2))
        #more client informations
        self.extendedInfo = RDPExtendedInfo(conditional = extendedInfoConditional)
        
class RDPExtendedInfo(CompositeType):
    '''
    add more client informations
    use for performance flag!!!
    '''
    def __init__(self, conditional):
        CompositeType.__init__(self, conditional = conditional)
        #is an ip v4 or v6 adresse
        self.clientAddressFamily = AfInet.AF_INET
        #len of adress field
        self.cbClientAddress = UInt16Le(lambda:sizeof(self.clientAddress))
        #adress of client
        self.clientAddress = UniString(readLen = self.cbClientAddress)
        #len of client directory
        self.cbClientDir = UInt16Le(lambda:sizeof(self.clientDir))
        #self client directory
        self.clientDir = UniString(readLen = self.cbClientDir)
        #TODO make tiomezone
        #self.performanceFlags = PerfFlag.PERF_DISABLE_WALLPAPER | PerfFlag.PERF_DISABLE_MENUANIMATIONS | PerfFlag.PERF_DISABLE_CURSOR_SHADOW

class ShareControlHeader(CompositeType):
    '''
    @see: http://msdn.microsoft.com/en-us/library/cc240576.aspx
    '''
    def __init__(self, totalLength):
        '''
        constructor
        @param totalLength: total length of pdu packet
        '''
        CompositeType.__init__(self)
        #share control header
        self.totalLength = UInt16Le(totalLength)
        self.pduType = UInt16Le()
        self.PDUSource = UInt16Le()
    
class Capability(CompositeType):
    '''
    @see: http://msdn.microsoft.com/en-us/library/cc240486.aspx
    '''
    def __init__(self):
        CompositeType.__init__(self)
        self.capabilitySetType = UInt16Le()
        self.lengthCapability = UInt16Le(lambda:sizeof(self))
        self.generalCapability = GeneralCapability(conditional = lambda:self.capabilitySetType == CapsType.CAPSTYPE_GENERAL)
        self.bitmapCapability = BitmapCapability(conditional = lambda:self.capabilitySetType == CapsType.CAPSTYPE_BITMAP)
        self.capabilityData = String(readLen = UInt16Le(lambda:self.lengthCapability.value - 4), conditional = lambda:not self.capabilitySetType in [CapsType.CAPSTYPE_GENERAL, CapsType.CAPSTYPE_BITMAP])
        
class GeneralCapability(CompositeType):
    '''
    @see: http://msdn.microsoft.com/en-us/library/cc240549.aspx
    '''
    def __init__(self, conditional = lambda:True):
        CompositeType.__init__(self, conditional = conditional)
        self.osMajorType = UInt16Le()
        self.osMinorType = UInt16Le()
        self.protocolVersion = UInt16Le(0x0200, constant = True)
        self.pad2octetsA = UInt16Le()
        self.generalCompressionTypes = UInt16Le(0, constant = True)
        self.extraFlags = UInt16Le()
        self.updateCapabilityFlag = UInt16Le(0, constant = True)
        self.remoteUnshareFlag = UInt16Le(0, constant = True)
        self.generalCompressionLevel = UInt16Le(0, constant = True)
        self.refreshRectSupport = UInt8()
        self.suppressOutputSupport = UInt8()
        
class BitmapCapability(CompositeType):
    '''
    @see: http://msdn.microsoft.com/en-us/library/cc240554.aspx
    '''
    def __init__(self, conditional = lambda:True):
        CompositeType.__init__(self, conditional = conditional)
        self.preferredBitsPerPixel = UInt16Le()
        self.receive1BitPerPixel = UInt16Le(0x0001)
        self.receive4BitsPerPixel = UInt16Le(0x0001)
        self.receive8BitsPerPixel = UInt16Le(0x0001)
        self.desktopWidth = UInt16Le()
        self.desktopHeight = UInt16Le()
        self.pad2octets = UInt16Le()
        self.desktopResizeFlag = UInt16Le()
        self.bitmapCompressionFlag = UInt16Le()
        self.highColorFlags = UInt8(0)
        self.drawingFlags = UInt8()
        self.multipleRectangleSupport = UInt16Le(0x0001, constant = True)
        self.pad2octetsB = UInt16Le()

class DemandActivePDU(CompositeType):
    '''
    @see: http://msdn.microsoft.com/en-us/library/cc240485.aspx
    '''
    def __init__(self):
        CompositeType.__init__(self)
        self.shareControlHeader = ShareControlHeader(lambda:sizeof(self))
        self.shareId = UInt32Le()
        self.lengthSourceDescriptor = UInt16Le(lambda:sizeof(self.sourceDescriptor))
        self.lengthCombinedCapabilities = UInt16Le(lambda:(sizeof(self.numberCapabilities) + sizeof(self.pad2Octets) + sizeof(self.capabilitySets)))
        self.sourceDescriptor = String("rdpy", readLen = self.lengthSourceDescriptor)
        self.numberCapabilities = UInt16Le(lambda:len(self.capabilitySets._array))
        self.pad2Octets = UInt16Le()
        self.capabilitySets = ArrayType(Capability, readLen = self.numberCapabilities)
        self.sessionId = UInt32Le()
        
class ConfirmActivePDU(CompositeType):
    '''
    @see: http://msdn.microsoft.com/en-us/library/cc240488.aspx
    '''
    def __init__(self):
        CompositeType.__init__(self)
        self.shareControlHeader = ShareControlHeader(lambda:sizeof(self))
        self.shareId = UInt32Le()
        self.originatorId = UInt16Le(0x03EA, constant = True)
        self.lengthSourceDescriptor = UInt16Le(lambda:sizeof(self.sourceDescriptor))
        self.lengthCombinedCapabilities = UInt16Le(lambda:(sizeof(self.numberCapabilities) + sizeof(self.pad2Octets) + sizeof(self.capabilitySets)))
        self.sourceDescriptor = String("rdpy", readLen = self.lengthSourceDescriptor)
        self.numberCapabilities = UInt16Le(lambda:len(self.capabilitySets._array))
        self.pad2Octets = UInt16Le()
        self.capabilitySets = ArrayType(Capability, readLen = self.numberCapabilities)

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
        self._info = RDPInfo(extendedInfoConditional = lambda:self._transport._serverSettings.core.rdpVersion == gcc.Version.RDP_VERSION_5_PLUS)
        #server capabilities
        self._serverCapabilities = {}
        #client capabilities
        self._clientCapabilities = {}
        
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
        send a logon info packet
        '''
        #always send extended info because rdpy only accept rdp version 5 and more
        self._transport.send(self._channelId, (SecurityFlag.SEC_INFO_PKT, UInt16Le(), self._info))
    
    def recvLicenceInfo(self, data):
        '''
        read license info packet and check if is a valid client info
        @param data: Stream
        '''
        securityFlag = UInt16Le()
        securityFlagHi = UInt16Le()
        data.readType((securityFlag, securityFlagHi))
        
        if securityFlag & SecurityFlag.SEC_LICENSE_PKT != SecurityFlag.SEC_LICENSE_PKT:
            raise InvalidExpectedDataException("waiting license packet")
        
        validClientPdu = lic.LicPacket()
        data.readType(validClientPdu)
        
        if not validClientPdu.errorMessage._is_readed:
            raise InvalidExpectedDataException("waiting valid client pdu : rdpy doesn't support licensing neg")
        
        if not (validClientPdu.errorMessage.dwErrorCode == lic.ErrorCode.STATUS_VALID_CLIENT and validClientPdu.errorMessage.dwStateTransition == lic.StateTransition.ST_NO_TRANSITION):
            raise InvalidExpectedDataException("server refuse licensing negotiation")
        
        self.setNextState(self.recvDemandActivePDU)
        
    def recvDemandActivePDU(self, data):
        '''
        receive demand active PDU which contains 
        server capabilities. In this version of RDPY only
        restricted group of capabilities are used.
        send confirm active PDU
        '''
        demandActivePDU = DemandActivePDU()
        data.readType(demandActivePDU)
        
        for cap in demandActivePDU.capabilitySets._array:
            self._serverCapabilities[cap.capabilitySetType] = cap
        
        confirmActivePDU = ConfirmActivePDU()
        confirmActivePDU.capabilitySets._array = self._clientCapabilities.values()
        
        self._transport.send(self._channelId, confirmActivePDU)