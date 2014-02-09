'''
@author: sylvain
'''

from rdpy.network.layer import LayerAutomata
from rdpy.network.type import CompositeType, UniString, String, UInt8, UInt16Le, UInt16Be, UInt32Le, sizeof, ArrayType
from rdpy.network.const import ConstAttributes, TypeAttributes
from rdpy.network.error import InvalidExpectedDataException

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
    
@ConstAttributes
@TypeAttributes(UInt16Le)  
class MajorType(object):
    '''
    use in general capability
    @see: http://msdn.microsoft.com/en-us/library/cc240549.aspx
    '''
    OSMAJORTYPE_UNSPECIFIED = 0x0000
    OSMAJORTYPE_WINDOWS = 0x0001
    OSMAJORTYPE_OS2 = 0x0002
    OSMAJORTYPE_MACINTOSH = 0x0003
    OSMAJORTYPE_UNIX = 0x0004
    OSMAJORTYPE_IOS = 0x0005
    OSMAJORTYPE_OSX = 0x0006
    OSMAJORTYPE_ANDROID = 0x0007
    
@ConstAttributes
@TypeAttributes(UInt16Le)    
class MinorType(object):
    '''
    use in general capability
    @see: http://msdn.microsoft.com/en-us/library/cc240549.aspx
    '''
    OSMINORTYPE_UNSPECIFIED = 0x0000
    OSMINORTYPE_WINDOWS_31X = 0x0001
    OSMINORTYPE_WINDOWS_95 = 0x0002
    OSMINORTYPE_WINDOWS_NT = 0x0003
    OSMINORTYPE_OS2_V21 = 0x0004
    OSMINORTYPE_POWER_PC = 0x0005
    OSMINORTYPE_MACINTOSH = 0x0006
    OSMINORTYPE_NATIVE_XSERVER = 0x0007
    OSMINORTYPE_PSEUDO_XSERVER = 0x0008
    OSMINORTYPE_WINDOWS_RT = 0x0009

@ConstAttributes
@TypeAttributes(UInt16Le)  
class GeneralExtraFlag(object):
    '''
    use in general capability
    @see: http://msdn.microsoft.com/en-us/library/cc240549.aspx
    '''
    FASTPATH_OUTPUT_SUPPORTED = 0x0001
    NO_BITMAP_COMPRESSION_HDR = 0x0400
    LONG_CREDENTIALS_SUPPORTED = 0x0004
    AUTORECONNECT_SUPPORTED = 0x0008
    ENC_SALTED_CHECKSUM = 0x0010
    
@ConstAttributes
@TypeAttributes(UInt8)   
class Boolean(object):
    FALSE = 0x00
    TRUE = 0x01

@ConstAttributes
@TypeAttributes(UInt16Le)  
class OrderFlag(object):
    '''
    use in order capability
    @see: http://msdn.microsoft.com/en-us/library/cc240556.aspx
    '''
    NEGOTIATEORDERSUPPORT = 0x0002
    ZEROBOUNDSDELTASSUPPORT = 0x0008
    COLORINDEXSUPPORT = 0x0020
    SOLIDPATTERNBRUSHONLY = 0x0040
    ORDERFLAGS_EXTRA_FLAGS = 0x0080
    
@ConstAttributes
@TypeAttributes(UInt8) 
class Order(object):
    '''
    drawing orders supported
    use in order capability
    @see: http://msdn.microsoft.com/en-us/library/cc240556.aspx
    '''
    TS_NEG_DSTBLT_INDEX = 0x00
    TS_NEG_PATBLT_INDEX = 0x01
    TS_NEG_SCRBLT_INDEX = 0x02
    TS_NEG_MEMBLT_INDEX = 0x03
    TS_NEG_MEM3BLT_INDEX = 0x04
    TS_NEG_DRAWNINEGRID_INDEX = 0x07
    TS_NEG_LINETO_INDEX = 0x08
    TS_NEG_MULTI_DRAWNINEGRID_INDEX = 0x09
    TS_NEG_SAVEBITMAP_INDEX = 0x0B
    TS_NEG_MULTIDSTBLT_INDEX = 0x0F
    TS_NEG_MULTIPATBLT_INDEX = 0x10
    TS_NEG_MULTISCRBLT_INDEX = 0x11
    TS_NEG_MULTIOPAQUERECT_INDEX = 0x12
    TS_NEG_FAST_INDEX_INDEX = 0x13
    TS_NEG_POLYGON_SC_INDEX = 0x14
    TS_NEG_POLYGON_CB_INDEX = 0x15
    TS_NEG_POLYLINE_INDEX = 0x16
    TS_NEG_FAST_GLYPH_INDEX = 0x18
    TS_NEG_ELLIPSE_SC_INDEX = 0x19
    TS_NEG_ELLIPSE_CB_INDEX = 0x1A
    TS_NEG_INDEX_INDEX = 0x1B
    
@ConstAttributes
@TypeAttributes(UInt16Le)     
class OrderEx(object):
    '''
    extension orders
    use in order capability
    '''
    ORDERFLAGS_EX_CACHE_BITMAP_REV3_SUPPORT = 0x0002
    ORDERFLAGS_EX_ALTSEC_FRAME_MARKER_SUPPORT = 0x0004
    
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
        self.flag = InfoFlag.INFO_MOUSE | InfoFlag.INFO_UNICODE | InfoFlag.INFO_LOGONERRORS | InfoFlag.INFO_LOGONNOTIFY | InfoFlag.INFO_ENABLEWINDOWSKEY | InfoFlag.INFO_DISABLECTRLALTDEL
        self.cbDomain = UInt16Le(lambda:sizeof(self.domain) - 2)
        self.cbUserName = UInt16Le(lambda:sizeof(self.userName) - 2)
        self.cbPassword = UInt16Le(lambda:sizeof(self.password) - 2)
        self.cbAlternateShell = UInt16Le(lambda:sizeof(self.alternateShell) - 2)
        self.cbWorkingDir = UInt16Le(lambda:sizeof(self.workingDir) - 2)
        #microsoft domain
        self.domain = UniString(readLen = UInt16Le(lambda:self.cbDomain.value - 2))
        self.userName = UniString(readLen = UInt16Le(lambda:self.cbUserName.value - 2))
        self.password = UniString(readLen = UInt16Le(lambda:self.cbPassword.value - 2))
        #shell execute at start of session
        self.alternateShell = UniString(readLen = UInt16Le(lambda:self.cbAlternateShell.value - 2))
        #working directory for session
        self.workingDir = UniString(readLen = UInt16Le(lambda:self.cbWorkingDir.value - 2))
        self.extendedInfo = RDPExtendedInfo(conditional = extendedInfoConditional)
        
class RDPExtendedInfo(CompositeType):
    '''
    add more client informations
    use for performance flag!!!
    '''
    def __init__(self, conditional):
        CompositeType.__init__(self, conditional = conditional)
        self.clientAddressFamily = AfInet.AF_INET
        self.cbClientAddress = UInt16Le(lambda:sizeof(self.clientAddress))
        self.clientAddress = UniString(readLen = self.cbClientAddress)
        self.cbClientDir = UInt16Le(lambda:sizeof(self.clientDir))
        self.clientDir = UniString(readLen = self.cbClientDir)
        #TODO make tiomezone
        #self.performanceFlags = PerfFlag.PERF_DISABLE_WALLPAPER | PerfFlag.PERF_DISABLE_MENUANIMATIONS | PerfFlag.PERF_DISABLE_CURSOR_SHADOW

class ShareControlHeader(CompositeType):
    '''
    PDU share control header
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
    A capability
    @see: http://msdn.microsoft.com/en-us/library/cc240486.aspx
    '''
    def __init__(self):
        CompositeType.__init__(self)
        self.capabilitySetType = UInt16Le()
        self.lengthCapability = UInt16Le(lambda:sizeof(self))
        self.generalCapability = GeneralCapability(conditional = lambda:self.capabilitySetType == CapsType.CAPSTYPE_GENERAL)
        self.bitmapCapability = BitmapCapability(conditional = lambda:self.capabilitySetType == CapsType.CAPSTYPE_BITMAP)
        self.orderCapability = OrderCapability(conditional = lambda:self.capabilitySetType == CapsType.CAPSTYPE_ORDER)
        self.capabilityData = String(readLen = UInt16Le(lambda:self.lengthCapability.value - 4), conditional = lambda:not self.capabilitySetType in [CapsType.CAPSTYPE_GENERAL, CapsType.CAPSTYPE_BITMAP, CapsType.CAPSTYPE_ORDER])
        
class GeneralCapability(CompositeType):
    '''
    General capability (protocol version and compression mode)
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
    Bitmap format Capability
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
        
class OrderCapability(CompositeType):
    '''
    Order capability list all drawing order supported
    @see: http://msdn.microsoft.com/en-us/library/cc240556.aspx
    '''
    def __init__(self, conditional = lambda:True):
        CompositeType.__init__(self, conditional = conditional)
        self.terminalDescriptor = String("\x00" * 16)
        self.pad4octetsA = UInt32Le(0)
        self.desktopSaveXGranularity = UInt16Le(1)
        self.desktopSaveYGranularity = UInt16Le(20)
        self.pad2octetsA = UInt16Le(0)
        self.maximumOrderLevel = UInt16Le(1)
        self.numberFonts = UInt16Le(0)
        self.orderFlags = UInt16Le(0)
        self.orderSupport = ArrayType(UInt8, [0 for i in range(0,31)])
        self.textFlags = UInt16Le()
        self.orderSupportExFlags = UInt16Le()
        self.pad4octetsB = UInt32Le()
        self.desktopSaveSize = UInt32Le(480 * 480)
        self.pad2octetsC = UInt16Le()
        self.pad2octetsD = UInt16Le()
        self.textANSICodePage = UInt16Le(0)
        self.pad2octetsE = UInt16Le()
        
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

class SIL(LayerAutomata):
    '''
    Session information layer
    Global channel for mcs that handle session
    identification user, licensing management, and capabilities exchange
    '''
    def __init__(self, mode):
        '''
        Constructor
        '''
        LayerAutomata.__init__(self, mode, None)
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
        
        self.sendConfirmActivePDU()
        
    def sendConfirmActivePDU(self):
        '''
        send all client capabilities
        '''
        #init general capability
        capability = Capability()
        capability.capabilitySetType = CapsType.CAPSTYPE_GENERAL
        capability.generalCapability.osMajorType = MajorType.OSMAJORTYPE_UNIX
        capability.generalCapability.osMinorType = MinorType.OSMINORTYPE_UNSPECIFIED
        capability.generalCapability.extraFlags = GeneralExtraFlag.LONG_CREDENTIALS_SUPPORTED
        self._clientCapabilities[capability.capabilitySetType] = capability
        
        #make active PDU packet
        confirmActivePDU = ConfirmActivePDU()
        confirmActivePDU.capabilitySets._array = self._clientCapabilities.values()
        self._transport.send(self._channelId, confirmActivePDU)