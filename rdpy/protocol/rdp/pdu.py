'''
@author: sylvain
'''

from rdpy.network.layer import LayerAutomata
from rdpy.network.type import CompositeType, UniString, String, UInt8, UInt16Le, UInt16Be, UInt32Le, sizeof, ArrayType, FactoryType
from rdpy.network.const import ConstAttributes, TypeAttributes
from rdpy.network.error import InvalidExpectedDataException, ErrorReportedFromPeer

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
    '''
    data pdu type primary index
    @see: http://msdn.microsoft.com/en-us/library/cc240576.aspx
    '''
    PDUTYPE_DEMANDACTIVEPDU = 0x11
    PDUTYPE_CONFIRMACTIVEPDU = 0x13
    PDUTYPE_DEACTIVATEALLPDU = 0x16
    PDUTYPE_DATAPDU = 0x17
    PDUTYPE_SERVER_REDIR_PKT = 0x1A

@ConstAttributes
@TypeAttributes(UInt8)  
class PDUType2(object):
    '''
    data pdu type secondary index
    @see: http://msdn.microsoft.com/en-us/library/cc240577.aspx
    '''
    PDUTYPE2_UPDATE = 0x02
    PDUTYPE2_CONTROL = 0x14
    PDUTYPE2_POINTER = 0x1B
    PDUTYPE2_INPUT = 0x1C
    PDUTYPE2_SYNCHRONIZE = 0x1F
    PDUTYPE2_REFRESH_RECT = 0x21
    PDUTYPE2_PLAY_SOUND = 0x22
    PDUTYPE2_SUPPRESS_OUTPUT = 0x23
    PDUTYPE2_SHUTDOWN_REQUEST = 0x24
    PDUTYPE2_SHUTDOWN_DENIED = 0x25
    PDUTYPE2_SAVE_SESSION_INFO = 0x26
    PDUTYPE2_FONTLIST = 0x27
    PDUTYPE2_FONTMAP = 0x28
    PDUTYPE2_SET_KEYBOARD_INDICATORS = 0x29
    PDUTYPE2_BITMAPCACHE_PERSISTENT_LIST = 0x2B
    PDUTYPE2_BITMAPCACHE_ERROR_PDU = 0x2C
    PDUTYPE2_SET_KEYBOARD_IME_STATUS = 0x2D
    PDUTYPE2_OFFSCRCACHE_ERROR_PDU = 0x2E
    PDUTYPE2_SET_ERROR_INFO_PDU = 0x2F
    PDUTYPE2_DRAWNINEGRID_ERROR_PDU = 0x30
    PDUTYPE2_DRAWGDIPLUS_ERROR_PDU = 0x31
    PDUTYPE2_ARC_STATUS_PDU = 0x32
    PDUTYPE2_STATUS_INFO_PDU = 0x36
    PDUTYPE2_MONITOR_LAYOUT_PDU = 0x37
    
@ConstAttributes
@TypeAttributes(UInt8) 
class StreamId(object):
    '''
    stream priority
    @see: http://msdn.microsoft.com/en-us/library/cc240577.aspx
    '''
    STREAM_UNDEFINED = 0x00
    STREAM_LOW = 0x01
    STREAM_MED = 0x02
    STREAM_HI = 0x04
    
@ConstAttributes
@TypeAttributes(UInt8)   
class CompressionOrder(object):
    '''
    pdu compression order
    @see: http://msdn.microsoft.com/en-us/library/cc240577.aspx
    '''
    CompressionTypeMask = 0x0F
    PACKET_COMPRESSED = 0x20
    PACKET_AT_FRONT = 0x40
    PACKET_FLUSHED = 0x80

class CompressionType(object):
    '''
    pdu compression type
    @see: http://msdn.microsoft.com/en-us/library/cc240577.aspx
    '''
    PACKET_COMPR_TYPE_8K = 0x0
    PACKET_COMPR_TYPE_64K = 0x1
    PACKET_COMPR_TYPE_RDP6 = 0x2
    PACKET_COMPR_TYPE_RDP61 = 0x3
    
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

@ConstAttributes
@TypeAttributes(UInt16Le)
class Action(object):
    '''
    Action flag use in Control PDU packet
    @see: http://msdn.microsoft.com/en-us/library/cc240492.aspx
    '''
    CTRLACTION_REQUEST_CONTROL = 0x0001
    CTRLACTION_GRANTED_CONTROL = 0x0002
    CTRLACTION_DETACH = 0x0003
    CTRLACTION_COOPERATE = 0x0004
    
@ConstAttributes
@TypeAttributes(UInt16Le)
class PersistentKeyListFlag(object):
    '''
    use to determine the number of persistent key packet
    @see: http://msdn.microsoft.com/en-us/library/cc240495.aspx
    '''
    PERSIST_FIRST_PDU = 0x01
    PERSIST_LAST_PDU = 0x02

@ConstAttributes
@TypeAttributes(UInt32Le)
class ErrorInfo(object):
    '''
    Error code use in Error info pdu
    @see: http://msdn.microsoft.com/en-us/library/cc240544.aspx
    '''
    ERRINFO_RPC_INITIATED_DISCONNECT = 0x00000001
    ERRINFO_RPC_INITIATED_LOGOFF = 0x00000002
    ERRINFO_IDLE_TIMEOUT = 0x00000003
    ERRINFO_LOGON_TIMEOUT = 0x00000004
    ERRINFO_DISCONNECTED_BY_OTHERCONNECTION = 0x00000005
    ERRINFO_OUT_OF_MEMORY = 0x00000006
    ERRINFO_SERVER_DENIED_CONNECTION = 0x00000007
    ERRINFO_SERVER_INSUFFICIENT_PRIVILEGES = 0x00000009
    ERRINFO_SERVER_FRESH_CREDENTIALS_REQUIRED = 0x0000000A
    ERRINFO_RPC_INITIATED_DISCONNECT_BYUSER = 0x0000000B
    ERRINFO_LOGOFF_BY_USER = 0x0000000C
    ERRINFO_LICENSE_INTERNAL = 0x00000100
    ERRINFO_LICENSE_NO_LICENSE_SERVER = 0x00000101
    ERRINFO_LICENSE_NO_LICENSE = 0x00000102
    ERRINFO_LICENSE_BAD_CLIENT_MSG = 0x00000103
    ERRINFO_LICENSE_HWID_DOESNT_MATCH_LICENSE = 0x00000104
    ERRINFO_LICENSE_BAD_CLIENT_LICENSE = 0x00000105
    ERRINFO_LICENSE_CANT_FINISH_PROTOCOL = 0x00000106
    ERRINFO_LICENSE_CLIENT_ENDED_PROTOCOL = 0x00000107
    ERRINFO_LICENSE_BAD_CLIENT_ENCRYPTION = 0x00000108
    ERRINFO_LICENSE_CANT_UPGRADE_LICENSE = 0x00000109
    ERRINFO_LICENSE_NO_REMOTE_CONNECTIONS = 0x0000010A
    ERRINFO_CB_DESTINATION_NOT_FOUND = 0x0000400
    ERRINFO_CB_LOADING_DESTINATION = 0x0000402
    ERRINFO_CB_REDIRECTING_TO_DESTINATION = 0x0000404
    ERRINFO_CB_SESSION_ONLINE_VM_WAKE = 0x0000405
    ERRINFO_CB_SESSION_ONLINE_VM_BOOT = 0x0000406
    ERRINFO_CB_SESSION_ONLINE_VM_NO_DNS = 0x0000407
    ERRINFO_CB_DESTINATION_POOL_NOT_FREE = 0x0000408
    ERRINFO_CB_CONNECTION_CANCELLED = 0x0000409
    ERRINFO_CB_CONNECTION_ERROR_INVALID_SETTINGS = 0x0000410
    ERRINFO_CB_SESSION_ONLINE_VM_BOOT_TIMEOUT = 0x0000411
    ERRINFO_CB_SESSION_ONLINE_VM_SESSMON_FAILED = 0x0000412
    ERRINFO_UNKNOWNPDUTYPE2 = 0x000010C9
    ERRINFO_UNKNOWNPDUTYPE = 0x000010CA
    ERRINFO_DATAPDUSEQUENCE = 0x000010CB
    ERRINFO_CONTROLPDUSEQUENCE = 0x000010CD
    ERRINFO_INVALIDCONTROLPDUACTION = 0x000010CE
    ERRINFO_INVALIDINPUTPDUTYPE = 0x000010CF
    ERRINFO_INVALIDINPUTPDUMOUSE = 0x000010D0
    ERRINFO_INVALIDREFRESHRECTPDU = 0x000010D1
    ERRINFO_CREATEUSERDATAFAILED = 0x000010D2
    ERRINFO_CONNECTFAILED =0x000010D3
    ERRINFO_CONFIRMACTIVEWRONGSHAREID = 0x000010D4
    ERRINFO_CONFIRMACTIVEWRONGORIGINATOR = 0x000010D5
    ERRINFO_PERSISTENTKEYPDUBADLENGTH = 0x000010DA
    ERRINFO_PERSISTENTKEYPDUILLEGALFIRST = 0x000010DB
    ERRINFO_PERSISTENTKEYPDUTOOMANYTOTALKEYS = 0x000010DC
    ERRINFO_PERSISTENTKEYPDUTOOMANYCACHEKEYS = 0x000010DD
    ERRINFO_INPUTPDUBADLENGTH = 0x000010DE
    ERRINFO_BITMAPCACHEERRORPDUBADLENGTH = 0x000010DF
    ERRINFO_SECURITYDATATOOSHORT = 0x000010E0
    ERRINFO_VCHANNELDATATOOSHORT = 0x000010E1
    ERRINFO_SHAREDATATOOSHORT = 0x000010E2
    ERRINFO_BADSUPRESSOUTPUTPDU = 0x000010E3
    ERRINFO_CONFIRMACTIVEPDUTOOSHORT = 0x000010E5
    ERRINFO_CAPABILITYSETTOOSMALL = 0x000010E7
    ERRINFO_CAPABILITYSETTOOLARGE = 0x000010E8
    ERRINFO_NOCURSORCACHE = 0x000010E9
    ERRINFO_BADCAPABILITIES = 0x000010EA
    ERRINFO_VIRTUALCHANNELDECOMPRESSIONERR = 0x000010EC
    ERRINFO_INVALIDVCCOMPRESSIONTYPE = 0x000010ED
    ERRINFO_INVALIDCHANNELID = 0x000010EF
    ERRINFO_VCHANNELSTOOMANY = 0x000010F0
    ERRINFO_REMOTEAPPSNOTENABLED = 0x000010F3
    ERRINFO_CACHECAPNOTSET = 0x000010F4
    ERRINFO_BITMAPCACHEERRORPDUBADLENGTH2 = 0x000010F5
    ERRINFO_OFFSCRCACHEERRORPDUBADLENGTH = 0x000010F6
    ERRINFO_DNGCACHEERRORPDUBADLENGTH = 0x000010F7
    ERRINFO_GDIPLUSPDUBADLENGTH = 0x000010F8
    ERRINFO_SECURITYDATATOOSHORT2 = 0x00001111
    ERRINFO_SECURITYDATATOOSHORT3 = 0x00001112
    ERRINFO_SECURITYDATATOOSHORT4 = 0x00001113
    ERRINFO_SECURITYDATATOOSHORT5 = 0x00001114
    ERRINFO_SECURITYDATATOOSHORT6 = 0x00001115
    ERRINFO_SECURITYDATATOOSHORT7 = 0x00001116
    ERRINFO_SECURITYDATATOOSHORT8 = 0x00001117
    ERRINFO_SECURITYDATATOOSHORT9 = 0x00001118
    ERRINFO_SECURITYDATATOOSHORT10 = 0x00001119
    ERRINFO_SECURITYDATATOOSHORT11 = 0x0000111A
    ERRINFO_SECURITYDATATOOSHORT12 = 0x0000111B
    ERRINFO_SECURITYDATATOOSHORT13 = 0x0000111C
    ERRINFO_SECURITYDATATOOSHORT14 = 0x0000111D
    ERRINFO_SECURITYDATATOOSHORT15 = 0x0000111E
    ERRINFO_SECURITYDATATOOSHORT16 = 0x0000111F
    ERRINFO_SECURITYDATATOOSHORT17 = 0x00001120
    ERRINFO_SECURITYDATATOOSHORT18 = 0x00001121
    ERRINFO_SECURITYDATATOOSHORT19 = 0x00001122
    ERRINFO_SECURITYDATATOOSHORT20 = 0x00001123
    ERRINFO_SECURITYDATATOOSHORT21 = 0x00001124
    ERRINFO_SECURITYDATATOOSHORT22 = 0x00001125
    ERRINFO_SECURITYDATATOOSHORT23 = 0x00001126
    ERRINFO_BADMONITORDATA = 0x00001129
    ERRINFO_VCDECOMPRESSEDREASSEMBLEFAILED = 0x0000112A
    ERRINFO_VCDATATOOLONG = 0x0000112B
    ERRINFO_BAD_FRAME_ACK_DATA = 0x0000112C
    ERRINFO_GRAPHICSMODENOTSUPPORTED = 0x0000112D
    ERRINFO_GRAPHICSSUBSYSTEMRESETFAILED = 0x0000112E
    ERRINFO_GRAPHICSSUBSYSTEMFAILED = 0x0000112F
    ERRINFO_TIMEZONEKEYNAMELENGTHTOOSHORT = 0x00001130
    ERRINFO_TIMEZONEKEYNAMELENGTHTOOLONG = 0x00001131
    ERRINFO_DYNAMICDSTDISABLEDFIELDMISSING = 0x00001132
    ERRINFO_VCDECODINGERROR = 0x00001133
    ERRINFO_UPDATESESSIONKEYFAILED = 0x00001191
    ERRINFO_DECRYPTFAILED = 0x00001192
    ERRINFO_ENCRYPTFAILED = 0x00001193
    ERRINFO_ENCPKGMISMATCH = 0x00001194
    ERRINFO_DECRYPTFAILED2 = 0x00001195
    
    _MESSAGES_ = {
     ERRINFO_RPC_INITIATED_DISCONNECT : "The disconnection was initiated by an administrative tool on the server in another session.",
     ERRINFO_RPC_INITIATED_LOGOFF : "The disconnection was due to a forced logoff initiated by an administrative tool on the server in another session.",
     ERRINFO_IDLE_TIMEOUT : "The idle session limit timer on the server has elapsed.",
     ERRINFO_LOGON_TIMEOUT : "The active session limit timer on the server has elapsed.",
     ERRINFO_DISCONNECTED_BY_OTHERCONNECTION : "Another user connected to the server, forcing the disconnection of the current connection.",
     ERRINFO_OUT_OF_MEMORY : "The server ran out of available memory resources.",
     ERRINFO_SERVER_DENIED_CONNECTION : "The server denied the connection.",
     ERRINFO_SERVER_INSUFFICIENT_PRIVILEGES : "The user cannot connect to the server due to insufficient access privileges.",
     ERRINFO_SERVER_FRESH_CREDENTIALS_REQUIRED : "The server does not accept saved user credentials and requires that the user enter their credentials for each connection.",
     ERRINFO_RPC_INITIATED_DISCONNECT_BYUSER : "The disconnection was initiated by an administrative tool on the server running in the user's session.",
     ERRINFO_LOGOFF_BY_USER : "The disconnection was initiated by the user logging off his or her session on the server.",
     ERRINFO_LICENSE_INTERNAL : "An internal error has occurred in the Terminal Services licensing component.",
     ERRINFO_LICENSE_NO_LICENSE_SERVER : "A Remote Desktop License Server ([MS-RDPELE] section 1.1) could not be found to provide a license.",
     ERRINFO_LICENSE_NO_LICENSE : "There are no Client Access Licenses ([MS-RDPELE] section 1.1) available for the target remote computer.",
     ERRINFO_LICENSE_BAD_CLIENT_MSG : "The remote computer received an invalid licensing message from the client.",
     ERRINFO_LICENSE_HWID_DOESNT_MATCH_LICENSE : "The Client Access License ([MS-RDPELE] section 1.1) stored by the client has been modified.",
     ERRINFO_LICENSE_BAD_CLIENT_LICENSE : "The Client Access License ([MS-RDPELE] section 1.1) stored by the client is in an invalid format",
     ERRINFO_LICENSE_CANT_FINISH_PROTOCOL : "Network problems have caused the licensing protocol ([MS-RDPELE] section 1.3.3) to be terminated.",
     ERRINFO_LICENSE_CLIENT_ENDED_PROTOCOL : "The client prematurely ended the licensing protocol ([MS-RDPELE] section 1.3.3).",
     ERRINFO_LICENSE_BAD_CLIENT_ENCRYPTION : "A licensing message ([MS-RDPELE] sections 2.2 and 5.1) was incorrectly encrypted.",
     ERRINFO_LICENSE_CANT_UPGRADE_LICENSE : "The Client Access License ([MS-RDPELE] section 1.1) stored by the client could not be upgraded or renewed.",
     ERRINFO_LICENSE_NO_REMOTE_CONNECTIONS : "The remote computer is not licensed to accept remote connections.",
     ERRINFO_CB_DESTINATION_NOT_FOUND : "The target endpoint could not be found.",
     ERRINFO_CB_LOADING_DESTINATION : "The target endpoint to which the client is being redirected is disconnecting from the Connection Broker.",
     ERRINFO_CB_REDIRECTING_TO_DESTINATION : "An error occurred while the connection was being redirected to the target endpoint.",
     ERRINFO_CB_SESSION_ONLINE_VM_WAKE : "An error occurred while the target endpoint (a virtual machine) was being awakened.",
     ERRINFO_CB_SESSION_ONLINE_VM_BOOT : "An error occurred while the target endpoint (a virtual machine) was being started.",
     ERRINFO_CB_SESSION_ONLINE_VM_NO_DNS : "The IP address of the target endpoint (a virtual machine) cannot be determined.",
     ERRINFO_CB_DESTINATION_POOL_NOT_FREE : "There are no available endpoints in the pool managed by the Connection Broker.",
     ERRINFO_CB_CONNECTION_CANCELLED : "Processing of the connection has been cancelled.",
     ERRINFO_CB_CONNECTION_ERROR_INVALID_SETTINGS : "The settings contained in the routingToken field of the X.224 Connection Request PDU (section 2.2.1.1) cannot be validated.",
     ERRINFO_CB_SESSION_ONLINE_VM_BOOT_TIMEOUT : "A time-out occurred while the target endpoint (a virtual machine) was being started.",
     ERRINFO_CB_SESSION_ONLINE_VM_SESSMON_FAILED : "A session monitoring error occurred while the target endpoint (a virtual machine) was being started.",
     ERRINFO_UNKNOWNPDUTYPE2 : "Unknown pduType2 field in a received Share Data Header (section 2.2.8.1.1.1.2).",
     ERRINFO_UNKNOWNPDUTYPE : "Unknown pduType field in a received Share Control Header (section 2.2.8.1.1.1.1).",
     ERRINFO_DATAPDUSEQUENCE : "An out-of-sequence Slow-Path Data PDU (section 2.2.8.1.1.1.1) has been received.",
     ERRINFO_CONTROLPDUSEQUENCE : "An out-of-sequence Slow-Path Non-Data PDU (section 2.2.8.1.1.1.1) has been received.",
     ERRINFO_INVALIDCONTROLPDUACTION : "A Control PDU (sections 2.2.1.15 and 2.2.1.16) has been received with an invalid action field.",
     ERRINFO_INVALIDINPUTPDUTYPE : "A Slow-Path Input Event (section 2.2.8.1.1.3.1.1) has been received with an invalid messageType field OR A Fast-Path Input Event (section 2.2.8.1.2.2) has been received with an invalid eventCode field",
     ERRINFO_INVALIDINPUTPDUMOUSE : "A Slow-Path Mouse Event (section 2.2.8.1.1.3.1.1.3) or Extended Mouse Event (section 2.2.8.1.1.3.1.1.4) has been received with an invalid pointerFlags field OR A Fast-Path Mouse Event (section 2.2.8.1.2.2.3) or Fast-Path Extended Mouse Event (section 2.2.8.1.2.2.4) has been received with an invalid pointerFlags field.",
     ERRINFO_INVALIDREFRESHRECTPDU : "An invalid Refresh Rect PDU (section 2.2.11.2) has been received.",
     ERRINFO_CREATEUSERDATAFAILED : "The server failed to construct the GCC Conference Create Response user data (section 2.2.1.4).",
     ERRINFO_CONNECTFAILED : "Processing during the Channel Connection phase of the RDP Connection Sequence (see section 1.3.1.1 for an overview of the RDP Connection Sequence phases) has failed.",
     ERRINFO_CONFIRMACTIVEWRONGSHAREID : "A Confirm Active PDU (section 2.2.1.13.2) was received from the client with an invalid shareId field.",
     ERRINFO_CONFIRMACTIVEWRONGORIGINATOR : "A Confirm Active PDU (section 2.2.1.13.2) was received from the client with an invalid originatorId field.",
     ERRINFO_PERSISTENTKEYPDUBADLENGTH : "There is not enough data to process a Persistent Key List PDU (section 2.2.1.17).",
     ERRINFO_PERSISTENTKEYPDUILLEGALFIRST : "A Persistent Key List PDU (section 2.2.1.17) marked as PERSIST_PDU_FIRST (0x01) was received after the reception of a prior Persistent Key List PDU also marked as PERSIST_PDU_FIRST.",
     ERRINFO_PERSISTENTKEYPDUTOOMANYTOTALKEYS : "A Persistent Key List PDU (section 2.2.1.17) was received which specified a total number of bitmap cache entries larger than 262144.",
     ERRINFO_PERSISTENTKEYPDUTOOMANYCACHEKEYS : "A Persistent Key List PDU (section 2.2.1.17) was received which specified an invalid total number of keys for a bitmap cache (the number of entries that can be stored within each bitmap cache is specified in the Revision 1 or 2 Bitmap Cache Capability Set (section 2.2.7.1.4) that is sent from client to server).",
     ERRINFO_INPUTPDUBADLENGTH : "There is not enough data to process Input Event PDU Data (section 2.2.8.1.1.3.1) or a Fast-Path Input Event PDU (section 2.2.8.1.2).",
     ERRINFO_BITMAPCACHEERRORPDUBADLENGTH : "There is not enough data to process the shareDataHeader, NumInfoBlocks, Pad1, and Pad2 fields of the Bitmap Cache Error PDU Data ([MS-RDPEGDI] section 2.2.2.3.1.1).",
     ERRINFO_SECURITYDATATOOSHORT : "The dataSignature field of the Fast-Path Input Event PDU (section 2.2.8.1.2) does not contain enough data OR The fipsInformation and dataSignature fields of the Fast-Path Input Event PDU (section 2.2.8.1.2) do not contain enough data.",
     ERRINFO_VCHANNELDATATOOSHORT : "There is not enough data in the Client Network Data (section 2.2.1.3.4) to read the virtual channel configuration data OR There is not enough data to read a complete Channel PDU Header (section 2.2.6.1.1).",
     ERRINFO_SHAREDATATOOSHORT : "There is not enough data to process Control PDU Data (section 2.2.1.15.1) OR There is not enough data to read a complete Share Control Header (section 2.2.8.1.1.1.1) OR There is not enough data to read a complete Share Data Header (section 2.2.8.1.1.1.2) of a Slow-Path Data PDU (section 2.2.8.1.1.1.1) OR There is not enough data to process Font List PDU Data (section 2.2.1.18.1).",
     ERRINFO_BADSUPRESSOUTPUTPDU : "There is not enough data to process Suppress Output PDU Data (section 2.2.11.3.1) OR The allowDisplayUpdates field of the Suppress Output PDU Data (section 2.2.11.3.1) is invalid.",
     ERRINFO_CONFIRMACTIVEPDUTOOSHORT : "There is not enough data to read the shareControlHeader, shareId, originatorId, lengthSourceDescriptor, and lengthCombinedCapabilities fields of the Confirm Active PDU Data (section 2.2.1.13.2.1) OR There is not enough data to read the sourceDescriptor, numberCapabilities, pad2Octets, and capabilitySets fields of the Confirm Active PDU Data (section 2.2.1.13.2.1).",
     ERRINFO_CAPABILITYSETTOOSMALL : "There is not enough data to read the capabilitySetType and the lengthCapability fields in a received Capability Set (section 2.2.1.13.1.1.1).",
     ERRINFO_CAPABILITYSETTOOLARGE : "A Capability Set (section 2.2.1.13.1.1.1) has been received with a lengthCapability field that contains a value greater than the total length of the data received.",
     ERRINFO_NOCURSORCACHE : "Both the colorPointerCacheSize and pointerCacheSize fields in the Pointer Capability Set (section 2.2.7.1.5) are set to zero OR The pointerCacheSize field in the Pointer Capability Set (section 2.2.7.1.5) is not present, and the colorPointerCacheSize field is set to zero.",
     ERRINFO_BADCAPABILITIES : "The capabilities received from the client in the Confirm Active PDU (section 2.2.1.13.2) were not accepted by the server.",
     ERRINFO_VIRTUALCHANNELDECOMPRESSIONERR : "An error occurred while using the bulk compressor (section 3.1.8 and [MS-RDPEGDI] section 3.1.8) to decompress a Virtual Channel PDU (section 2.2.6.1).",
     ERRINFO_INVALIDVCCOMPRESSIONTYPE : "An invalid bulk compression package was specified in the flags field of the Channel PDU Header (section 2.2.6.1.1).",
     ERRINFO_INVALIDCHANNELID : "An invalid MCS channel ID was specified in the mcsPdu field of the Virtual Channel PDU (section 2.2.6.1).",
     ERRINFO_VCHANNELSTOOMANY : "The client requested more than the maximum allowed 31 static virtual channels in the Client Network Data (section 2.2.1.3.4).",
     ERRINFO_REMOTEAPPSNOTENABLED : "The INFO_RAIL flag (0x00008000) MUST be set in the flags field of the Info Packet (section 2.2.1.11.1.1) as the session on the remote server can only host remote applications.",
     ERRINFO_CACHECAPNOTSET : "The client sent a Persistent Key List PDU (section 2.2.1.17) without including the prerequisite Revision 2 Bitmap Cache Capability Set (section 2.2.7.1.4.2) in the Confirm Active PDU (section 2.2.1.13.2).",
     ERRINFO_BITMAPCACHEERRORPDUBADLENGTH2 : "The NumInfoBlocks field in the Bitmap Cache Error PDU Data is inconsistent with the amount of data in the Info field ([MS-RDPEGDI] section 2.2.2.3.1.1).",
     ERRINFO_OFFSCRCACHEERRORPDUBADLENGTH : "There is not enough data to process an Offscreen Bitmap Cache Error PDU ([MS-RDPEGDI] section 2.2.2.3.2).",
     ERRINFO_GDIPLUSPDUBADLENGTH : "There is not enough data to process a GDI+ Error PDU ([MS-RDPEGDI] section 2.2.2.3.4).",
     ERRINFO_SECURITYDATATOOSHORT2 : "There is not enough data to read a Basic Security Header (section 2.2.8.1.1.2.1).",
     ERRINFO_SECURITYDATATOOSHORT3 : "There is not enough data to read a Non-FIPS Security Header (section 2.2.8.1.1.2.2) or FIPS Security Header (section 2.2.8.1.1.2.3).",
     ERRINFO_SECURITYDATATOOSHORT4 : "There is not enough data to read the basicSecurityHeader and length fields of the Security Exchange PDU Data (section 2.2.1.10.1).",
     ERRINFO_SECURITYDATATOOSHORT5 : "There is not enough data to read the CodePage, flags, cbDomain, cbUserName, cbPassword, cbAlternateShell, cbWorkingDir, Domain, UserName, Password, AlternateShell, and WorkingDir fields in the Info Packet (section 2.2.1.11.1.1).",
     ERRINFO_SECURITYDATATOOSHORT6 : "There is not enough data to read the CodePage, flags, cbDomain, cbUserName, cbPassword, cbAlternateShell, and cbWorkingDir fields in the Info Packet (section 2.2.1.11.1.1).",
     ERRINFO_SECURITYDATATOOSHORT7 : "There is not enough data to read the clientAddressFamily and cbClientAddress fields in the Extended Info Packet (section 2.2.1.11.1.1.1).",
     ERRINFO_SECURITYDATATOOSHORT8 : "There is not enough data to read the clientAddress field in the Extended Info Packet (section 2.2.1.11.1.1.1).",
     ERRINFO_SECURITYDATATOOSHORT9 : "There is not enough data to read the cbClientDir field in the Extended Info Packet (section 2.2.1.11.1.1.1).",
     ERRINFO_SECURITYDATATOOSHORT10 : "There is not enough data to read the clientDir field in the Extended Info Packet (section 2.2.1.11.1.1.1).",
     ERRINFO_SECURITYDATATOOSHORT11 : "There is not enough data to read the clientTimeZone field in the Extended Info Packet (section 2.2.1.11.1.1.1).",
     ERRINFO_SECURITYDATATOOSHORT12 : "There is not enough data to read the clientSessionId field in the Extended Info Packet (section 2.2.1.11.1.1.1).",
     ERRINFO_SECURITYDATATOOSHORT13 : "There is not enough data to read the performanceFlags field in the Extended Info Packet (section 2.2.1.11.1.1.1).",
     ERRINFO_SECURITYDATATOOSHORT14 : "There is not enough data to read the cbAutoReconnectCookie field in the Extended Info Packet (section 2.2.1.11.1.1.1).",
     ERRINFO_SECURITYDATATOOSHORT15 : "There is not enough data to read the autoReconnectCookie field in the Extended Info Packet (section 2.2.1.11.1.1.1).",
     ERRINFO_SECURITYDATATOOSHORT16 : "The cbAutoReconnectCookie field in the Extended Info Packet (section 2.2.1.11.1.1.1) contains a value which is larger than the maximum allowed length of 128 bytes.",
     ERRINFO_SECURITYDATATOOSHORT17 : "There is not enough data to read the clientAddressFamily and cbClientAddress fields in the Extended Info Packet (section 2.2.1.11.1.1.1).",
     ERRINFO_SECURITYDATATOOSHORT18 : "There is not enough data to read the clientAddress field in the Extended Info Packet (section 2.2.1.11.1.1.1).",
     ERRINFO_SECURITYDATATOOSHORT19 : "There is not enough data to read the cbClientDir field in the Extended Info Packet (section 2.2.1.11.1.1.1).",
     ERRINFO_SECURITYDATATOOSHORT20 : "There is not enough data to read the clientDir field in the Extended Info Packet (section 2.2.1.11.1.1.1).",
     ERRINFO_SECURITYDATATOOSHORT21 : "There is not enough data to read the clientTimeZone field in the Extended Info Packet (section 2.2.1.11.1.1.1).",
     ERRINFO_SECURITYDATATOOSHORT22 : "There is not enough data to read the clientSessionId field in the Extended Info Packet (section 2.2.1.11.1.1.1).",
     ERRINFO_SECURITYDATATOOSHORT23 : "There is not enough data to read the Client Info PDU Data (section 2.2.1.11.1).",
     ERRINFO_BADMONITORDATA : "The monitorCount field in the Client Monitor Data (section 2.2.1.3.6) is invalid.",
     ERRINFO_VCDECOMPRESSEDREASSEMBLEFAILED : "The server-side decompression buffer is invalid, or the size of the decompressed VC data exceeds the chunking size specified in the Virtual Channel Capability Set (section 2.2.7.1.10).",
     ERRINFO_VCDATATOOLONG : "The size of a received Virtual Channel PDU (section 2.2.6.1) exceeds the chunking size specified in the Virtual Channel Capability Set (section 2.2.7.1.10).",
    }

@ConstAttributes
@TypeAttributes(UInt16Le) 
class InputFlags(object):
    '''
    Input flag use in input capability
    @see:  http://msdn.microsoft.com/en-us/library/cc240563.aspx
    '''
    INPUT_FLAG_SCANCODES = 0x0001
    INPUT_FLAG_MOUSEX = 0x0004
    INPUT_FLAG_FASTPATH_INPUT = 0x0008
    INPUT_FLAG_UNICODE = 0x0010
    INPUT_FLAG_FASTPATH_INPUT2 = 0x0020
    INPUT_FLAG_UNUSED1 = 0x0040
    INPUT_FLAG_UNUSED2 = 0x0080
    TS_INPUT_FLAG_MOUSE_HWHEEL = 0x0100

@ConstAttributes
@TypeAttributes(UInt32Le)
class BrushSupport(object):
    '''
    Brush support of client
    @see: http://msdn.microsoft.com/en-us/library/cc240564.aspx
    '''
    BRUSH_DEFAULT = 0x00000000
    BRUSH_COLOR_8x8 = 0x00000001
    BRUSH_COLOR_FULL = 0x00000002

@ConstAttributes
@TypeAttributes(UInt16Le)  
class GlyphSupport(object):
    '''
    Use by glyph order
    @see: http://msdn.microsoft.com/en-us/library/cc240565.aspx
    '''
    GLYPH_SUPPORT_NONE = 0x0000
    GLYPH_SUPPORT_PARTIAL = 0x0001
    GLYPH_SUPPORT_FULL = 0x0002
    GLYPH_SUPPORT_ENCODE = 0x0003

@ConstAttributes
@TypeAttributes(UInt32Le)    
class OffscreenSupportLevel(object):
    '''
    Use to determine offscreen cache level supported
    @see: http://msdn.microsoft.com/en-us/library/cc240550.aspx
    '''
    FALSE = 0x00000000
    TRUE = 0x00000001

@ConstAttributes
@TypeAttributes(UInt32Le) 
class VirtualChannelCompressionFlag(object):
    '''
    Use to determine virtual channel compression
    @see: http://msdn.microsoft.com/en-us/library/cc240551.aspx
    '''
    VCCAPS_NO_COMPR = 0x00000000
    VCCAPS_COMPR_SC = 0x00000001
    VCCAPS_COMPR_CS_8K = 0x00000002

@ConstAttributes
@TypeAttributes(UInt16Le)   
class SoundFlag(object):
    '''
    Use in sound capability to inform it
    @see: http://msdn.microsoft.com/en-us/library/cc240552.aspx
    '''
    NONE = 0x0000
    SOUND_BEEPS_FLAG = 0x0001
    
class RDPInfo(CompositeType):
    '''
    client informations
    contains credentials (very important packet)
    @see: http://msdn.microsoft.com/en-us/library/cc240475.aspx
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
    def __init__(self, totalLength, pduType, userId):
        '''
        constructor
        @param totalLength: total length of pdu packet
        '''
        CompositeType.__init__(self)
        #share control header
        self.totalLength = UInt16Le(totalLength)
        self.pduType = UInt16Le(pduType.value, constant = True)
        self.PDUSource = UInt16Le(userId.value + 1001)
        
class ShareDataHeader(CompositeType):
    '''
    PDU share data header
    @see: http://msdn.microsoft.com/en-us/library/cc240577.aspx
    '''
    def __init__(self, size, pduType2, userId = UInt16Le(), shareId = UInt32Le()):
        CompositeType.__init__(self)
        self.shareControlHeader = ShareControlHeader(size, PDUType.PDUTYPE_DATAPDU, userId)
        self.shareId = shareId
        self.pad1 = UInt8()
        self.streamId = StreamId.STREAM_LOW
        self.uncompressedLength = UInt16Le(lambda:(UInt16Le(size).value - 14))
        self.pduType2 = UInt8(pduType2.value, constant = True)
        self.compressedType = UInt8()
        self.compressedLength = UInt16Le()
        
class CacheEntry(CompositeType):
    '''
    Use in capability cache exchange
    @see: http://msdn.microsoft.com/en-us/library/cc240566.aspx
    '''
    def __init__(self):
        CompositeType.__init__(self)
        self.cacheEntries = UInt16Le()
        self.cacheMaximumCellSize = UInt16Le()
    
    
class Capability(CompositeType):
    '''
    A capability
    @see: http://msdn.microsoft.com/en-us/library/cc240486.aspx
    '''
    def __init__(self, capabilitySetType = UInt16Le(), capability = None):
        CompositeType.__init__(self)
        self.capabilitySetType = UInt16Le(capabilitySetType.value, constant = (not capability is None))
        self.lengthCapability = UInt16Le(lambda:sizeof(self))
        
        def CapabilityFactory():
            '''
            closure for capability factory
            '''
            if self.capabilitySetType == CapsType.CAPSTYPE_GENERAL:
                return GeneralCapability(readLen = UInt16Le(lambda:self.lengthCapability.value - 4))
            elif self.capabilitySetType == CapsType.CAPSTYPE_BITMAP:
                return BitmapCapability(readLen = UInt16Le(lambda:self.lengthCapability.value - 4))
            elif self.capabilitySetType == CapsType.CAPSTYPE_ORDER:
                return OrderCapability(readLen = UInt16Le(lambda:self.lengthCapability.value - 4))
            elif self.capabilitySetType == CapsType.CAPSTYPE_BITMAPCACHE:
                return BitmapCacheCapability(readLen = UInt16Le(lambda:self.lengthCapability.value - 4))
            elif self.capabilitySetType == CapsType.CAPSTYPE_POINTER:
                return PointerCapability(readLen = UInt16Le(lambda:self.lengthCapability.value - 4))
            elif self.capabilitySetType == CapsType.CAPSTYPE_INPUT:
                return InputCapability(readLen = UInt16Le(lambda:self.lengthCapability.value - 4))
            elif self.capabilitySetType == CapsType.CAPSTYPE_BRUSH:
                return BrushCapability(readLen = UInt16Le(lambda:self.lengthCapability.value - 4))
            elif self.capabilitySetType == CapsType.CAPSTYPE_GLYPHCACHE:
                return GlyphCapability(readLen = UInt16Le(lambda:self.lengthCapability.value - 4))
            elif self.capabilitySetType == CapsType.CAPSTYPE_OFFSCREENCACHE:
                return OffscreenBitmapCacheCapability(readLen = UInt16Le(lambda:self.lengthCapability.value - 4))
            elif self.capabilitySetType == CapsType.CAPSTYPE_VIRTUALCHANNEL:
                return VirtualChannelCapability(readLen = UInt16Le(lambda:self.lengthCapability.value - 4))
            elif self.capabilitySetType == CapsType.CAPSTYPE_SOUND:
                return SoundCapability(readLen = UInt16Le(lambda:self.lengthCapability.value - 4))
            elif self.capabilitySetType == CapsType.CAPSTYPE_CONTROL:
                return ControlCapability(readLen = UInt16Le(lambda:self.lengthCapability.value - 4))
            elif self.capabilitySetType == CapsType.CAPSTYPE_ACTIVATION:
                return WindowActivationCapability(readLen = UInt16Le(lambda:self.lengthCapability.value - 4))
            elif self.capabilitySetType == CapsType.CAPSTYPE_FONT:
                return FontCapability(readLen = UInt16Le(lambda:self.lengthCapability.value - 4))
            elif self.capabilitySetType == CapsType.CAPSTYPE_COLORCACHE:
                return ColorCacheCapability(readLen = UInt16Le(lambda:self.lengthCapability.value - 4))
            elif self.capabilitySetType == CapsType.CAPSTYPE_SHARE:
                return ShareCapability(readLen = UInt16Le(lambda:self.lengthCapability.value - 4))
            else:
                return String(readLen = UInt16Le(lambda:self.lengthCapability.value - 4))
        
        if capability is None:
            capability = CapabilityFactory
            
        self.capability = FactoryType(capability)
        
class GeneralCapability(CompositeType):
    '''
    General capability (protocol version and compression mode)
    client -> server
    server -> client
    @see: http://msdn.microsoft.com/en-us/library/cc240549.aspx
    '''
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
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
    client -> server
    server -> client
    @see: http://msdn.microsoft.com/en-us/library/cc240554.aspx
    '''
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.preferredBitsPerPixel = UInt16Le()
        self.receive1BitPerPixel = UInt16Le(0x0001)
        self.receive4BitsPerPixel = UInt16Le(0x0001)
        self.receive8BitsPerPixel = UInt16Le(0x0001)
        self.desktopWidth = UInt16Le()
        self.desktopHeight = UInt16Le()
        self.pad2octets = UInt16Le()
        self.desktopResizeFlag = UInt16Le()
        self.bitmapCompressionFlag = UInt16Le(0x0001, constant = True)
        self.highColorFlags = UInt8(0)
        self.drawingFlags = UInt8()
        self.multipleRectangleSupport = UInt16Le(0x0001, constant = True)
        self.pad2octetsB = UInt16Le()
        
class OrderCapability(CompositeType):
    '''
    Order capability list all drawing order supported
    client -> server
    server -> client
    @see: http://msdn.microsoft.com/en-us/library/cc240556.aspx
    '''
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.terminalDescriptor = String("\x00" * 16, readLen = UInt8(16))
        self.pad4octetsA = UInt32Le(0)
        self.desktopSaveXGranularity = UInt16Le(1)
        self.desktopSaveYGranularity = UInt16Le(20)
        self.pad2octetsA = UInt16Le(0)
        self.maximumOrderLevel = UInt16Le(1)
        self.numberFonts = UInt16Le()
        self.orderFlags = OrderFlag.NEGOTIATEORDERSUPPORT
        self.orderSupport = ArrayType(UInt8, init = [UInt8(0) for i in range (0, 32)],  readLen = UInt8(32))
        self.textFlags = UInt16Le()
        self.orderSupportExFlags = UInt16Le()
        self.pad4octetsB = UInt32Le()
        self.desktopSaveSize = UInt32Le(480 * 480)
        self.pad2octetsC = UInt16Le()
        self.pad2octetsD = UInt16Le()
        self.textANSICodePage = UInt16Le(0)
        self.pad2octetsE = UInt16Le()
        
class BitmapCacheCapability(CompositeType):
    '''
    Order use to cache bitmap very usefull
    client -> server
    @see: http://msdn.microsoft.com/en-us/library/cc240559.aspx
    '''
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.pad1 = UInt32Le()
        self.pad2 = UInt32Le()
        self.pad3 = UInt32Le()
        self.pad4 = UInt32Le()
        self.pad5 = UInt32Le()
        self.pad6 = UInt32Le()
        self.cache0Entries = UInt16Le()
        self.cache0MaximumCellSize = UInt16Le()
        self.cache1Entries = UInt16Le()
        self.cache1MaximumCellSize = UInt16Le()
        self.cache2Entries = UInt16Le()
        self.cache2MaximumCellSize = UInt16Le()
        
class PointerCapability(CompositeType):
    '''
    Use to indicate pointer handle of client
    Paint by server or per client
    client -> server
    server -> client
    @see: http://msdn.microsoft.com/en-us/library/cc240562.aspx
    '''
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.colorPointerFlag = UInt16Le()
        self.colorPointerCacheSize = UInt16Le()
        self.pointerCacheSize = UInt16Le()
        
class InputCapability(CompositeType):
    '''
    Use to indicate input capabilities
    client -> server
    server -> client
    @see: http://msdn.microsoft.com/en-us/library/cc240563.aspx
    '''
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.inputFlags = UInt16Le()
        self.pad2octetsA = UInt16Le()
        #same value as gcc.ClientCoreSettings.kbdLayout
        self.keyboardLayout = UInt32Le()
        #same value as gcc.ClientCoreSettings.keyboardType
        self.keyboardType = UInt32Le()
        #same value as gcc.ClientCoreSettings.keyboardSubType
        self.keyboardSubType = UInt32Le()
        #same value as gcc.ClientCoreSettings.keyboardFnKeys
        self.keyboardFunctionKey = UInt32Le()
        #same value as gcc.ClientCoreSettingrrs.imeFileName
        self.imeFileName = String("\x00" * 64, readLen = UInt8(64))
        
class BrushCapability(CompositeType):
    '''
    Use to indicate brush capability
    client -> server
    @see: http://msdn.microsoft.com/en-us/library/cc240564.aspx
    '''
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.brushSupportLevel = BrushSupport.BRUSH_DEFAULT
        
class GlyphCapability(CompositeType):
    '''
    Use in font order
    client -> server
    @see: http://msdn.microsoft.com/en-us/library/cc240565.aspx
    '''
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.glyphCache = ArrayType(CacheEntry, init = [CacheEntry() for i in range(0,10)], readLen = UInt8(10))
        self.fragCache = UInt32Le()
        #all fonts are sent with bitmap format (very expensive)
        self.glyphSupportLevel = GlyphSupport.GLYPH_SUPPORT_NONE
        self.pad2octets = UInt16Le()
        
class OffscreenBitmapCacheCapability(CompositeType):
    '''
    use to cached bitmap in offscreen area
    client -> server
    @see: http://msdn.microsoft.com/en-us/library/cc240550.aspx
    '''
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.offscreenSupportLevel = OffscreenSupportLevel.FALSE
        self.offscreenCacheSize = UInt16Le()
        self.offscreenCacheEntries = UInt16Le()
        
class VirtualChannelCapability(CompositeType):
    '''
    use to determine virtual channel compression
    client -> server
    server -> client
    @see: http://msdn.microsoft.com/en-us/library/cc240551.aspx
    '''
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.flags = VirtualChannelCompressionFlag.VCCAPS_NO_COMPR
        self.VCChunkSize = UInt32Le(optional = True)
        
class SoundCapability(CompositeType):
    '''
    use to exchange sound capability
    client -> server
    @see: http://msdn.microsoft.com/en-us/library/cc240552.aspx
    '''
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.soundFlags = SoundFlag.NONE
        self.pad2octetsA = UInt16Le()
        
class ControlCapability(CompositeType):
    '''
    client -> server but server ignore contents! Thanks krosoft for brandwidth
    @see: http://msdn.microsoft.com/en-us/library/cc240568.aspx
    '''
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.controlFlags = UInt16Le()
        self.remoteDetachFlag = UInt16Le()
        self.controlInterest = UInt16Le(0x0002)
        self.detachInterest = UInt16Le(0x0002)
    
class WindowActivationCapability(CompositeType):
    '''
    client -> server but server ignore contents! Thanks krosoft for brandwidth
    @see: http://msdn.microsoft.com/en-us/library/cc240569.aspx
    '''
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.helpKeyFlag = UInt16Le()
        self.helpKeyIndexFlag = UInt16Le()
        self.helpExtendedKeyFlag = UInt16Le()
        self.windowManagerKeyFlag = UInt16Le()
        
class FontCapability(CompositeType):
    '''
    use to indicate font support
    client -> server
    server -> client
    @see: http://msdn.microsoft.com/en-us/library/cc240571.aspx
    '''
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.fontSupportFlags = UInt16Le(0x0001)
        self.pad2octets = UInt16Le()
        
class ColorCacheCapability(CompositeType):
    '''
    client -> server
    server -> client
    @see: http://msdn.microsoft.com/en-us/library/cc241564.aspx
    '''
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.colorTableCacheSize = UInt16Le(0x0006)
        self.pad2octets = UInt16Le()
        
class ShareCapability(CompositeType):
    '''
    use to advertise channel id of server
    client -> server
    server -> client
    @see: http://msdn.microsoft.com/en-us/library/cc240570.aspx
    '''
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.nodeId = UInt16Le()
        self.pad2octets = UInt16Le()
        
class DemandActivePDU(CompositeType):
    '''
    @see: http://msdn.microsoft.com/en-us/library/cc240485.aspx
    main use for capabilities exchange server -> client
    '''
    def __init__(self, userId = UInt16Le()):
        CompositeType.__init__(self)
        self.shareControlHeader = ShareControlHeader(lambda:sizeof(self), PDUType.PDUTYPE_DEMANDACTIVEPDU, userId)
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
    main use for capabilities confirm client -> sever
    '''
    def __init__(self, userId = UInt16Le()):
        CompositeType.__init__(self)
        self.shareDataHeader = ShareControlHeader(lambda:sizeof(self), PDUType.PDUTYPE_CONFIRMACTIVEPDU, userId)
        self.shareId = UInt32Le()
        self.originatorId = UInt16Le(0x03EA, constant = True)
        self.lengthSourceDescriptor = UInt16Le(lambda:sizeof(self.sourceDescriptor))
        self.lengthCombinedCapabilities = UInt16Le(lambda:(sizeof(self.numberCapabilities) + sizeof(self.pad2Octets) + sizeof(self.capabilitySets)))
        self.sourceDescriptor = String("RDPY", readLen = self.lengthSourceDescriptor)
        self.numberCapabilities = UInt16Le(lambda:len(self.capabilitySets._array))
        self.pad2Octets = UInt16Le()
        self.capabilitySets = ArrayType(Capability, readLen = self.numberCapabilities)
        
class SynchronizePDU(CompositeType):
    '''
    @see http://msdn.microsoft.com/en-us/library/cc240490.aspx
    '''
    def __init__(self, userId = UInt16Le(), shareId = UInt32Le()):
        CompositeType.__init__(self)
        self.shareDataHeader = ShareDataHeader(lambda:sizeof(self), PDUType2.PDUTYPE2_SYNCHRONIZE, userId, shareId)
        self.messageType = UInt16Le(1, constant = True)
        self.targetUser = UInt16Le()
        
class ControlPDU(CompositeType):
    '''
    @see http://msdn.microsoft.com/en-us/library/cc240492.aspx
    '''
    def __init__(self, action, userId = UInt16Le(), shareId = UInt32Le()):
        CompositeType.__init__(self)
        self.shareDataHeader = ShareDataHeader(lambda:sizeof(self), PDUType2.PDUTYPE2_CONTROL, userId, shareId)
        self.action = UInt16Le(action.value, constant = True)
        self.grantId = UInt16Le()
        self.controlId = UInt32Le()

class PersistentListEntry(CompositeType):   
    '''
    use to record persistent key in PersistentListPDU
    @see: http://msdn.microsoft.com/en-us/library/cc240496.aspx
    '''  
    def __init__(self):
        CompositeType.__init__(self)
        self.key1 = UInt32Le()
        self.key2 = UInt32Le()
    
    
class PersistentListPDU(CompositeType):
    '''
    Use to indicate that bitmap cache was already
    fill with some keys from previous session
    @see: http://msdn.microsoft.com/en-us/library/cc240495.aspx
    '''
    def __init__(self, userId = UInt16Le(), shareId = UInt32Le()):
        CompositeType.__init__(self)
        self.shareControlHeader = ShareDataHeader(lambda:sizeof(self), PDUType2.PDUTYPE2_BITMAPCACHE_PERSISTENT_LIST, userId, shareId)
        self.numEntriesCache0 = UInt16Le()
        self.numEntriesCache1 = UInt16Le()
        self.numEntriesCache2 = UInt16Le()
        self.numEntriesCache3 = UInt16Le()
        self.numEntriesCache4 = UInt16Le()
        self.totalEntriesCache0 = UInt16Le()
        self.totalEntriesCache1 = UInt16Le()
        self.totalEntriesCache2 = UInt16Le()
        self.totalEntriesCache3 = UInt16Le()
        self.totalEntriesCache4 = UInt16Le()
        self.bitMask = UInt8()
        self.pad2 = UInt8()
        self.pad3 = UInt16Le()
        self.entries = ArrayType(PersistentListEntry, readLen = lambda:(self.numEntriesCache0 + self.numEntriesCache1 + self.numEntriesCache2 + self.numEntriesCache3 + self.numEntriesCache4))
        
class ErrorInfoPDU(CompositeType):
    '''
    Use to inform error in PDU layer
    @see: http://msdn.microsoft.com/en-us/library/cc240544.aspx
    '''
    def __init__(self):
        CompositeType.__init__(self)
        self.shareDataHeader = ShareDataHeader(lambda:sizeof(self), PDUType2.PDUTYPE2_SET_ERROR_INFO_PDU)
        #use to collect error info pdu
        self.errorInfo = UInt32Le()

class PDU(LayerAutomata):
    '''
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
        self._serverCapabilities = {
            CapsType.CAPSTYPE_GENERAL : Capability(CapsType.CAPSTYPE_GENERAL, GeneralCapability()),
            CapsType.CAPSTYPE_BITMAP : Capability(CapsType.CAPSTYPE_BITMAP, BitmapCapability()),
            CapsType.CAPSTYPE_ORDER : Capability(CapsType.CAPSTYPE_ORDER, OrderCapability()),
            CapsType.CAPSTYPE_POINTER : Capability(CapsType.CAPSTYPE_POINTER, PointerCapability()),
            CapsType.CAPSTYPE_INPUT : Capability(CapsType.CAPSTYPE_INPUT, InputCapability()),
            CapsType.CAPSTYPE_VIRTUALCHANNEL : Capability(CapsType.CAPSTYPE_VIRTUALCHANNEL, VirtualChannelCapability()),
            CapsType.CAPSTYPE_FONT : Capability(CapsType.CAPSTYPE_FONT, FontCapability()),
            CapsType.CAPSTYPE_COLORCACHE : Capability(CapsType.CAPSTYPE_COLORCACHE, ColorCacheCapability()),
            CapsType.CAPSTYPE_SHARE : Capability(CapsType.CAPSTYPE_SHARE, ShareCapability())
        }
        #client capabilities
        self._clientCapabilities = {
            CapsType.CAPSTYPE_GENERAL : Capability(CapsType.CAPSTYPE_GENERAL, GeneralCapability()),
            CapsType.CAPSTYPE_BITMAP : Capability(CapsType.CAPSTYPE_BITMAP, BitmapCapability()),
            CapsType.CAPSTYPE_ORDER : Capability(CapsType.CAPSTYPE_ORDER, OrderCapability()),
            CapsType.CAPSTYPE_BITMAPCACHE : Capability(CapsType.CAPSTYPE_BITMAPCACHE, BitmapCacheCapability()),
            CapsType.CAPSTYPE_POINTER : Capability(CapsType.CAPSTYPE_POINTER, PointerCapability()),
            CapsType.CAPSTYPE_INPUT : Capability(CapsType.CAPSTYPE_INPUT, InputCapability()),
            CapsType.CAPSTYPE_BRUSH : Capability(CapsType.CAPSTYPE_BRUSH, BrushCapability()),
            CapsType.CAPSTYPE_GLYPHCACHE : Capability(CapsType.CAPSTYPE_GLYPHCACHE, GlyphCapability()),
            CapsType.CAPSTYPE_OFFSCREENCACHE : Capability(CapsType.CAPSTYPE_OFFSCREENCACHE, OffscreenBitmapCacheCapability()),
            CapsType.CAPSTYPE_VIRTUALCHANNEL : Capability(CapsType.CAPSTYPE_VIRTUALCHANNEL, VirtualChannelCapability()),
            CapsType.CAPSTYPE_SOUND : Capability(CapsType.CAPSTYPE_SOUND, SoundCapability()),
            #CapsType.CAPSTYPE_CONTROL : Capability(CapsType.CAPSTYPE_CONTROL, ControlCapability()),
            #CapsType.CAPSTYPE_ACTIVATION : Capability(CapsType.CAPSTYPE_ACTIVATION, WindowActivationCapability()),
            #CapsType.CAPSTYPE_FONT : Capability(CapsType.CAPSTYPE_FONT, FontCapability()),
            #CapsType.CAPSTYPE_COLORCACHE : Capability(CapsType.CAPSTYPE_COLORCACHE, ColorCacheCapability()),
            #CapsType.CAPSTYPE_SHARE : Capability(CapsType.CAPSTYPE_SHARE, ShareCapability())
        }
        #share id between client and server
        self._shareId = UInt32Le()
        #mcs user id use for pdu packet
        self._userId = UInt16Be()
        
    def connect(self):
        '''
        connect event in client mode send logon info
        next state recv licence pdu
        '''
        #get user id from mcs layer
        self._userId = self._transport._userId
        
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
            raise InvalidExpectedDataException("Waiting license packet")
        
        validClientPdu = lic.LicPacket()
        data.readType(validClientPdu)
        
        if not validClientPdu.errorMessage._is_readed:
            raise InvalidExpectedDataException("Waiting valid client pdu : rdpy doesn't support licensing neg")
        
        if not (validClientPdu.errorMessage.dwErrorCode == lic.ErrorCode.STATUS_VALID_CLIENT and validClientPdu.errorMessage.dwStateTransition == lic.StateTransition.ST_NO_TRANSITION):
            raise InvalidExpectedDataException("Server refuse licensing negotiation")
        
        self.setNextState(self.recvDemandActivePDU)
        
    def readPDU(self, data, pdu):
        '''
        Try to read expected pdu or try to parse error info pdu
        '''
        try:
            data.readType(pdu)
        except Exception as e:
            #maybe an error message
            errorInfoPDU = ErrorInfoPDU()
            try:
                data.readType(errorInfoPDU)
                message = "Unknown code %s"%hex(errorInfoPDU.errorInfo.value)
                if ErrorInfo._MESSAGES_.has_key(errorInfoPDU.errorInfo):
                    message = ErrorInfo._MESSAGES_[errorInfoPDU.errorInfo]
                raise ErrorReportedFromPeer("Receive PDU Error info : %s"%message)
            except InvalidExpectedDataException:
                raise e
        
    def recvDemandActivePDU(self, data):
        '''
        receive demand active PDU which contains 
        server capabilities. In this version of RDPY only
        restricted group of capabilities are used.
        send confirm active PDU
        @param data: Stream
        '''
        demandActivePDU = DemandActivePDU()
        self.readPDU(data, demandActivePDU)
        
        self._shareId = demandActivePDU.shareId
        
        for cap in demandActivePDU.capabilitySets._array:
            self._serverCapabilities[cap.capabilitySetType] = cap
        
        self.sendConfirmActivePDU()
        
    def recvServerSynchronizePDU(self, data):
        '''
        receive from server 
        @param data: Stream from transport layer
        '''
        synchronizePDU = SynchronizePDU()
        self.readPDU(data, synchronizePDU)
        self.setNextState(self.recvServerControlCooperatePDU)
        
    def recvServerControlCooperatePDU(self, data):
        '''
        receive control cooperate pdu from server
        @param data: Stream from transport layer
        '''
        controlCooparatePDU = ControlPDU(Action.CTRLACTION_COOPERATE)
        self.readPDU(data, controlCooparatePDU)
        self.setNextState(self.recvServerControlGrantedPDU)
        
    def recvServerControlGrantedPDU(self, data):
        '''
        receive last control pdu the granted control pdu
        @param data: Stream from transport layer
        '''
        controlCooparatePDU = ControlPDU(Action.CTRLACTION_GRANTED_CONTROL)
        self.readPDU(data, controlCooparatePDU)
        
    def sendConfirmActivePDU(self):
        '''
        send all client capabilities
        '''
        #init general capability
        generalCapability = self._clientCapabilities[CapsType.CAPSTYPE_GENERAL].capability._value
        generalCapability.osMajorType = MajorType.OSMAJORTYPE_WINDOWS
        generalCapability.osMinorType = MinorType.OSMINORTYPE_WINDOWS_NT
        generalCapability.extraFlags = GeneralExtraFlag.LONG_CREDENTIALS_SUPPORTED | GeneralExtraFlag.NO_BITMAP_COMPRESSION_HDR
        
        #init bitmap capability
        bitmapCapability = self._clientCapabilities[CapsType.CAPSTYPE_BITMAP].capability._value
        bitmapCapability.preferredBitsPerPixel = self._transport._clientSettings.core.highColorDepth
        bitmapCapability.desktopWidth = self._transport._clientSettings.core.desktopWidth
        bitmapCapability.desktopHeight = self._transport._clientSettings.core.desktopHeight
         
        #init order capability
        orderCapability = self._clientCapabilities[CapsType.CAPSTYPE_ORDER].capability._value
        orderCapability.orderFlags |= OrderFlag.ZEROBOUNDSDELTASSUPPORT
        
        #init input capability
        inputCapability = self._clientCapabilities[CapsType.CAPSTYPE_INPUT].capability._value
        inputCapability.inputFlags = InputFlags.INPUT_FLAG_SCANCODES | InputFlags.INPUT_FLAG_MOUSEX | InputFlags.INPUT_FLAG_UNICODE
        inputCapability.keyboardLayout = self._transport._clientSettings.core.kbdLayout
        inputCapability.keyboardType = self._transport._clientSettings.core.keyboardType
        inputCapability.keyboardSubType = self._transport._clientSettings.core.keyboardSubType
        inputCapability.keyboardrFunctionKey = self._transport._clientSettings.core.keyboardFnKeys
        inputCapability.imeFileName = self._transport._clientSettings.core.imeFileName
        
        #make active PDU packet
        confirmActivePDU = ConfirmActivePDU(self._userId)
        confirmActivePDU.shareId = self._shareId
        confirmActivePDU.capabilitySets._array = self._clientCapabilities.values()
        self._transport.send(self._channelId, confirmActivePDU)
        #send synchronize
        self.sendClientFinalizeSynchronizePDU()
        
    def sendClientFinalizeSynchronizePDU(self):
        '''
        send a synchronize PDU from client to server
        '''
        synchronizePDU = SynchronizePDU(self._userId, self._shareId)
        synchronizePDU.targetUser = UInt16Le(self._channelId.value)
        self._transport.send(self._channelId, synchronizePDU)
        
        #ask for cooperation
        controlCooperatePDU = ControlPDU(Action.CTRLACTION_COOPERATE, self._userId, self._shareId)
        self._transport.send(self._channelId, controlCooperatePDU)
        
        #request control
        controlRequestPDU = ControlPDU(Action.CTRLACTION_REQUEST_CONTROL, self._userId, self._shareId)
        self._transport.send(self._channelId, controlRequestPDU)
        
        #send persistent list pdu
        persistentListPDU = PersistentListPDU(self._userId, self._shareId)
        persistentListPDU.bitMask = PersistentKeyListFlag.PERSIST_FIRST_PDU | PersistentKeyListFlag.PERSIST_LAST_PDU
        self._transport.send(self._channelId, persistentListPDU)
        
        self.setNextState(self.recvServerSynchronizePDU)
    