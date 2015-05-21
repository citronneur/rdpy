#
# Copyright (c) 2014-2015 Sylvain Peyrefitte
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
Implement the main graphic layer

In this layer are managed all mains bitmap update orders end user inputs
"""
from rdpy.core.type import CompositeType, CallableValue, String, UInt8, UInt16Le, UInt32Le, sizeof, ArrayType, FactoryType
from rdpy.core.error import InvalidExpectedDataException
import rdpy.core.log as log
import caps, order
 
class PDUType(object):
    """
    @summary: Data PDU type primary index
    @see: http://msdn.microsoft.com/en-us/library/cc240576.aspx
    """
    PDUTYPE_DEMANDACTIVEPDU = 0x11
    PDUTYPE_CONFIRMACTIVEPDU = 0x13
    PDUTYPE_DEACTIVATEALLPDU = 0x16
    PDUTYPE_DATAPDU = 0x17
    PDUTYPE_SERVER_REDIR_PKT = 0x1A
  
class PDUType2(object):
    """
    @summary: Data PDU type secondary index
    @see: http://msdn.microsoft.com/en-us/library/cc240577.aspx
    """
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
     
class StreamId(object):
    """
    @summary: Stream priority
    @see: http://msdn.microsoft.com/en-us/library/cc240577.aspx
    """
    STREAM_UNDEFINED = 0x00
    STREAM_LOW = 0x01
    STREAM_MED = 0x02
    STREAM_HI = 0x04
       
class CompressionOrder(object):
    """
    @summary: PDU compression order
    @see: http://msdn.microsoft.com/en-us/library/cc240577.aspx
    """
    CompressionTypeMask = 0x0F
    PACKET_COMPRESSED = 0x20
    PACKET_AT_FRONT = 0x40
    PACKET_FLUSHED = 0x80
    
class CompressionType(object):
    """
    @summary: PDU compression type
    @see: http://msdn.microsoft.com/en-us/library/cc240577.aspx
    """
    PACKET_COMPR_TYPE_8K = 0x0
    PACKET_COMPR_TYPE_64K = 0x1
    PACKET_COMPR_TYPE_RDP6 = 0x2
    PACKET_COMPR_TYPE_RDP61 = 0x3
    
class Action(object):
    """
    @summary: Action flag use in Control PDU packet
    @see: http://msdn.microsoft.com/en-us/library/cc240492.aspx
    """
    CTRLACTION_REQUEST_CONTROL = 0x0001
    CTRLACTION_GRANTED_CONTROL = 0x0002
    CTRLACTION_DETACH = 0x0003
    CTRLACTION_COOPERATE = 0x0004
    
class PersistentKeyListFlag(object):
    """
    @summary: Use to determine the number of persistent key packet
    @see: http://msdn.microsoft.com/en-us/library/cc240495.aspx
    """
    PERSIST_FIRST_PDU = 0x01
    PERSIST_LAST_PDU = 0x02

class BitmapFlag(object):
    """
    @summary: Use in bitmap update PDU
    @see: http://msdn.microsoft.com/en-us/library/cc240612.aspx
    """
    BITMAP_COMPRESSION = 0x0001
    NO_BITMAP_COMPRESSION_HDR = 0x0400
 
class UpdateType(object):
    """
    @summary: Use in update PDU to determine which type of update
    @see: http://msdn.microsoft.com/en-us/library/cc240608.aspx
    """
    UPDATETYPE_ORDERS = 0x0000
    UPDATETYPE_BITMAP = 0x0001
    UPDATETYPE_PALETTE = 0x0002
    UPDATETYPE_SYNCHRONIZE = 0x0003
    
class InputMessageType(object):
    """
    @summary: Use in slow-path input PDU
    @see: http://msdn.microsoft.com/en-us/library/cc240583.aspx
    """
    INPUT_EVENT_SYNC = 0x0000
    INPUT_EVENT_UNUSED = 0x0002
    INPUT_EVENT_SCANCODE = 0x0004
    INPUT_EVENT_UNICODE = 0x0005
    INPUT_EVENT_MOUSE = 0x8001
    INPUT_EVENT_MOUSEX = 0x8002
    
class PointerFlag(object):
    """
    @summary: Use in Pointer event
    @see: http://msdn.microsoft.com/en-us/library/cc240586.aspx
    """
    PTRFLAGS_HWHEEL = 0x0400
    PTRFLAGS_WHEEL = 0x0200
    PTRFLAGS_WHEEL_NEGATIVE = 0x0100
    WheelRotationMask = 0x01FF
    PTRFLAGS_MOVE = 0x0800
    PTRFLAGS_DOWN = 0x8000
    PTRFLAGS_BUTTON1 = 0x1000
    PTRFLAGS_BUTTON2 = 0x2000
    PTRFLAGS_BUTTON3 = 0x4000
    
class KeyboardFlag(object):
    """
    @summary: Use in scan code key event
    @see: http://msdn.microsoft.com/en-us/library/cc240584.aspx
    """
    KBDFLAGS_EXTENDED = 0x0100
    KBDFLAGS_DOWN = 0x4000
    KBDFLAGS_RELEASE = 0x8000
    
class FastPathUpdateType(object):
    """
    @summary: Use in Fast Path update packet
    @see: http://msdn.microsoft.com/en-us/library/cc240622.aspx
    """
    FASTPATH_UPDATETYPE_ORDERS = 0x0
    FASTPATH_UPDATETYPE_BITMAP = 0x1
    FASTPATH_UPDATETYPE_PALETTE = 0x2
    FASTPATH_UPDATETYPE_SYNCHRONIZE = 0x3
    FASTPATH_UPDATETYPE_SURFCMDS = 0x4
    FASTPATH_UPDATETYPE_PTR_NULL = 0x5
    FASTPATH_UPDATETYPE_PTR_DEFAULT = 0x6
    FASTPATH_UPDATETYPE_PTR_POSITION = 0x8
    FASTPATH_UPDATETYPE_COLOR = 0x9
    FASTPATH_UPDATETYPE_CACHED = 0xA
    FASTPATH_UPDATETYPE_POINTER = 0xB
    
class FastPathOutputCompression(object):
    """
    @summary: Flag for compression
    @see: http://msdn.microsoft.com/en-us/library/cc240622.aspx
    """
    FASTPATH_OUTPUT_COMPRESSION_USED = 0x2
    
class Display(object):
    """
    @summary: Use in supress output PDU
    @see: http://msdn.microsoft.com/en-us/library/cc240648.aspx
    """
    SUPPRESS_DISPLAY_UPDATES = 0x00
    ALLOW_DISPLAY_UPDATES = 0x01
    
class ToogleFlag(object):
    """
    @summary: Use to known state of keyboard
    @see: https://msdn.microsoft.com/en-us/library/cc240588.aspx
    """
    TS_SYNC_SCROLL_LOCK = 0x00000001
    TS_SYNC_NUM_LOCK = 0x00000002
    TS_SYNC_CAPS_LOCK = 0x00000004
    TS_SYNC_KANA_LOCK = 0x00000008
    
class ErrorInfo(object):
    """
    @summary: Error code use in Error info PDU
    @see: http://msdn.microsoft.com/en-us/library/cc240544.aspx
    """
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
    
class ShareControlHeader(CompositeType):
    """
    @summary: PDU share control header
    @see: http://msdn.microsoft.com/en-us/library/cc240576.aspx
    """
    def __init__(self, totalLength, pduType, userId):
        """
        @summary: Set pduType as constant
        @param totalLength: total length of PDU packet
        """
        CompositeType.__init__(self)
        #share control header
        self.totalLength = UInt16Le(totalLength)
        self.pduType = UInt16Le(pduType)
        #for xp sp3 and deactiveallpdu PDUSource may not be present
        self.PDUSource = UInt16Le(userId, optional = True)
        
class ShareDataHeader(CompositeType):
    """
    @summary: PDU share data header
    @see: http://msdn.microsoft.com/en-us/library/cc240577.aspx
    """
    def __init__(self, size, pduType2 = 0, shareId = 0):
        CompositeType.__init__(self)
        self.shareId = UInt32Le(shareId)
        self.pad1 = UInt8()
        self.streamId = UInt8(StreamId.STREAM_LOW)
        self.uncompressedLength = UInt16Le(lambda:(UInt16Le(size).value - 8))
        self.pduType2 = UInt8(pduType2)
        self.compressedType = UInt8()
        self.compressedLength = UInt16Le()
        
class PDU(CompositeType):
    """
    @summary: Main PDU message
    """
    def __init__(self, userId = 0, pduMessage = None):
        CompositeType.__init__(self)
        self.shareControlHeader = ShareControlHeader(lambda:sizeof(self), lambda:pduMessage.__class__._PDUTYPE_, userId)
        
        def PDUMessageFactory():
            """
            @summary: build message in accordance of type self.shareControlHeader.pduType.value
            """
            for c in [DemandActivePDU, ConfirmActivePDU, DataPDU, DeactiveAllPDU]:
                if self.shareControlHeader.pduType.value == c._PDUTYPE_:
                    return c(readLen = CallableValue(self.shareControlHeader.totalLength.value - sizeof(self.shareControlHeader)))
            log.debug("unknown PDU type : %s"%hex(self.shareControlHeader.pduType.value))
            #read entire packet
            return String(readLen = CallableValue(self.shareControlHeader.totalLength.value - sizeof(self.shareControlHeader)))
            
        if pduMessage is None:
            pduMessage = FactoryType(PDUMessageFactory)
        elif not "_PDUTYPE_" in  pduMessage.__class__.__dict__:
            raise InvalidExpectedDataException("Try to send an invalid PDU")
        
        self.pduMessage = pduMessage
        
class DemandActivePDU(CompositeType):
    """
    @see: http://msdn.microsoft.com/en-us/library/cc240485.aspx
    @summary: Main use for capabilities exchange server -> client
    """
    #may declare the PDU type
    _PDUTYPE_ = PDUType.PDUTYPE_DEMANDACTIVEPDU
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.shareId = UInt32Le()
        self.lengthSourceDescriptor = UInt16Le(lambda:sizeof(self.sourceDescriptor))
        self.lengthCombinedCapabilities = UInt16Le(lambda:(sizeof(self.numberCapabilities) + sizeof(self.pad2Octets) + sizeof(self.capabilitySets)))
        self.sourceDescriptor = String("rdpy", readLen = self.lengthSourceDescriptor)
        self.numberCapabilities = UInt16Le(lambda:len(self.capabilitySets._array))
        self.pad2Octets = UInt16Le()
        self.capabilitySets = ArrayType(caps.Capability, readLen = self.numberCapabilities)
        self.sessionId = UInt32Le()
        
class ConfirmActivePDU(CompositeType):
    """
    @see: http://msdn.microsoft.com/en-us/library/cc240488.aspx
    @summary: Main use for capabilities confirm client -> sever
    """
    #may declare the PDU type
    _PDUTYPE_ = PDUType.PDUTYPE_CONFIRMACTIVEPDU
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.shareId = UInt32Le()
        self.originatorId = UInt16Le(0x03EA, constant = True)
        self.lengthSourceDescriptor = UInt16Le(lambda:sizeof(self.sourceDescriptor))
        self.lengthCombinedCapabilities = UInt16Le(lambda:(sizeof(self.numberCapabilities) + sizeof(self.pad2Octets) + sizeof(self.capabilitySets)))
        self.sourceDescriptor = String("rdpy", readLen = self.lengthSourceDescriptor)
        self.numberCapabilities = UInt16Le(lambda:len(self.capabilitySets._array))
        self.pad2Octets = UInt16Le()
        self.capabilitySets = ArrayType(caps.Capability, readLen = self.numberCapabilities)
        
class DeactiveAllPDU(CompositeType):
    """
    @summary: Use to signal already connected session
    @see: http://msdn.microsoft.com/en-us/library/cc240536.aspx
    """
    #may declare the PDU type
    _PDUTYPE_ = PDUType.PDUTYPE_DEACTIVATEALLPDU
    
    def __init__(self, readLen = None):
        #in old version this packet is empty i don't know
        #and not specified
        CompositeType.__init__(self, optional = True, readLen = readLen)
        self.shareId = UInt32Le()
        self.lengthSourceDescriptor = UInt16Le(lambda:sizeof(self.sourceDescriptor))
        self.sourceDescriptor = String("rdpy", readLen = self.lengthSourceDescriptor)

class DataPDU(CompositeType):
    """
    @summary: Generic PDU packet use after connection sequence
    """
    #may declare the PDU type
    _PDUTYPE_ = PDUType.PDUTYPE_DATAPDU
    
    def __init__(self, pduData = None, shareId = 0, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.shareDataHeader = ShareDataHeader(lambda:sizeof(self), lambda:self.pduData.__class__._PDUTYPE2_, shareId)
        
        def PDUDataFactory():
            """
            @summary: Create object in accordance self.shareDataHeader.pduType2 value
            """
            for c in [UpdateDataPDU, SynchronizeDataPDU, ControlDataPDU, ErrorInfoDataPDU, FontListDataPDU, FontMapDataPDU, PersistentListPDU, ClientInputEventPDU, ShutdownDeniedPDU, ShutdownRequestPDU, SupressOutputDataPDU, SaveSessionInfoPDU]:
                if self.shareDataHeader.pduType2.value == c._PDUTYPE2_:
                    return c(readLen = CallableValue(readLen.value - sizeof(self.shareDataHeader)))
            log.debug("unknown PDU data type : %s"%hex(self.shareDataHeader.pduType2.value))
            return String(readLen = CallableValue(readLen.value - sizeof(self.shareDataHeader)))
            
        if pduData is None:
            pduData = FactoryType(PDUDataFactory)
        elif not "_PDUTYPE2_" in  pduData.__class__.__dict__:
            raise InvalidExpectedDataException("Try to send an invalid data PDU")
            
        self.pduData = pduData
        
class SynchronizeDataPDU(CompositeType):
    """
    @see http://msdn.microsoft.com/en-us/library/cc240490.aspx
    """
    _PDUTYPE2_ = PDUType2.PDUTYPE2_SYNCHRONIZE
    
    def __init__(self, targetUser = 0, readLen = None):
        """
        @param targetUser: MCS Channel ID
        """
        CompositeType.__init__(self, readLen = readLen)
        self.messageType = UInt16Le(1, constant = True)
        self.targetUser = UInt16Le(targetUser)
        
class ControlDataPDU(CompositeType):
    """
    @see http://msdn.microsoft.com/en-us/library/cc240492.aspx
    """
    _PDUTYPE2_ = PDUType2.PDUTYPE2_CONTROL
    
    def __init__(self, action = None, readLen = None):
        """
        @param action: Action macro
        @param readLen: Max length to read
        """
        CompositeType.__init__(self, readLen = readLen)
        self.action = UInt16Le(action, constant = True) if not action is None else UInt16Le()
        self.grantId = UInt16Le()
        self.controlId = UInt32Le()
        
class ErrorInfoDataPDU(CompositeType):
    """
    @summary: Use to inform error in PDU layer
    @see: http://msdn.microsoft.com/en-us/library/cc240544.aspx
    """
    _PDUTYPE2_ = PDUType2.PDUTYPE2_SET_ERROR_INFO_PDU
    
    def __init__(self, errorInfo = 0, readLen = None):
        """
        @param errorInfo: ErrorInfo macro
        @param readLen: Max length to read
        """
        CompositeType.__init__(self, readLen = readLen)
        #use to collect error info PDU
        self.errorInfo = UInt32Le(errorInfo)
        
class FontListDataPDU(CompositeType):
    """
    @summary: Use to indicate list of font. Deprecated packet
    client -> server
    @see: http://msdn.microsoft.com/en-us/library/cc240498.aspx
    """
    _PDUTYPE2_ = PDUType2.PDUTYPE2_FONTLIST
    
    def __init__(self, readLen = None):
        """
        @param readLen: Max read length
        """
        CompositeType.__init__(self, readLen = readLen)
        self.numberFonts = UInt16Le()
        self.totalNumFonts = UInt16Le()
        self.listFlags = UInt16Le(0x0003)
        self.entrySize = UInt16Le(0x0032)
        
class FontMapDataPDU(CompositeType):
    """
    @summary: Use to indicate map of font. Deprecated packet (maybe the same as FontListDataPDU)
    server -> client
    @see: http://msdn.microsoft.com/en-us/library/cc240498.aspx
    """
    _PDUTYPE2_ = PDUType2.PDUTYPE2_FONTMAP
    
    def __init__(self, readLen = None):
        """
        @param readLen: Max read length
        """
        CompositeType.__init__(self, readLen = readLen)
        self.numberEntries = UInt16Le()
        self.totalNumEntries = UInt16Le()
        self.mapFlags = UInt16Le(0x0003)
        self.entrySize = UInt16Le(0x0004)
        
class PersistentListEntry(CompositeType):   
    """
    @summary: Use to record persistent key in PersistentListPDU
    @see: http://msdn.microsoft.com/en-us/library/cc240496.aspx
    """  
    def __init__(self):
        CompositeType.__init__(self)
        self.key1 = UInt32Le()
        self.key2 = UInt32Le()
    
class PersistentListPDU(CompositeType):
    """
    @summary: Use to indicate that bitmap cache was already
    Fill with some keys from previous session
    @see: http://msdn.microsoft.com/en-us/library/cc240495.aspx
    """
    _PDUTYPE2_ = PDUType2.PDUTYPE2_BITMAPCACHE_PERSISTENT_LIST
    
    def __init__(self, userId = 0, shareId = 0, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
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
        self.entries = ArrayType(PersistentListEntry, readLen = CallableValue(lambda:(self.numEntriesCache0 + self.numEntriesCache1 + self.numEntriesCache2 + self.numEntriesCache3 + self.numEntriesCache4)))

class ClientInputEventPDU(CompositeType):
    """
    @summary: PDU use to send client inputs in slow path mode
    @see: http://msdn.microsoft.com/en-us/library/cc746160.aspx
    """
    _PDUTYPE2_ = PDUType2.PDUTYPE2_INPUT
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.numEvents = UInt16Le(lambda:len(self.slowPathInputEvents._array))
        self.pad2Octets = UInt16Le()
        self.slowPathInputEvents = ArrayType(SlowPathInputEvent, readLen = self.numEvents)     

class ShutdownRequestPDU(CompositeType):
    """
    @summary: PDU use to signal that the session will be closed
    client -> server
    """  
    _PDUTYPE2_ = PDUType2.PDUTYPE2_SHUTDOWN_REQUEST
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
             
class ShutdownDeniedPDU(CompositeType):
    """
    @summary: PDU use to signal which the session will be closed is connected
    server -> client
    """  
    _PDUTYPE2_ = PDUType2.PDUTYPE2_SHUTDOWN_DENIED
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)

class InclusiveRectangle(CompositeType):
    """
    @see: http://msdn.microsoft.com/en-us/library/cc240643.aspx
    """
    def __init__(self, conditional = lambda:True):
        CompositeType.__init__(self, conditional = conditional)
        self.left = UInt16Le()
        self.top = UInt16Le()
        self.right = UInt16Le()
        self.bottom = UInt16Le()
        
class SupressOutputDataPDU(CompositeType):
    """
    @see: http://msdn.microsoft.com/en-us/library/cc240648.aspx
    """
    _PDUTYPE2_ = PDUType2.PDUTYPE2_SUPPRESS_OUTPUT
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.allowDisplayUpdates = UInt8()
        self.pad3Octets = (UInt8(), UInt8(), UInt8())
        self.desktopRect = InclusiveRectangle(conditional = lambda:(self.allowDisplayUpdates.value == Display.ALLOW_DISPLAY_UPDATES))
        
class RefreshRectPDU(CompositeType):
    """
    @see: http://msdn.microsoft.com/en-us/library/cc240646.aspx
    """
    _PDUTYPE2_ = PDUType2.PDUTYPE2_REFRESH_RECT
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.numberOfAreas = UInt8(lambda:len(self.areasToRefresh._array))
        self.pad3Octets = (UInt8(), UInt8(), UInt8())
        self.areasToRefresh = ArrayType(InclusiveRectangle, readLen = self.numberOfAreas)

class UpdateDataPDU(CompositeType):
    """
    @summary: Update data PDU use by server to inform update image or palet
    for example
    @see: http://msdn.microsoft.com/en-us/library/cc240608.aspx
    """
    _PDUTYPE2_ = PDUType2.PDUTYPE2_UPDATE
    
    def __init__(self, updateData = None, readLen = None):
        """
        @param updateType: UpdateType macro
        @param updateData: Update data PDU in accordance with updateType (BitmapUpdateDataPDU)
        @param readLen: Max length to read
        """
        CompositeType.__init__(self, readLen = readLen)
        self.updateType = UInt16Le(lambda:updateData.__class__._UPDATE_TYPE_)
        
        def UpdateDataFactory():
            """
            @summary: Create object in accordance self.updateType value
            """
            for c in [BitmapUpdateDataPDU]:
                if self.updateType.value == c._UPDATE_TYPE_:
                    return c(readLen = CallableValue(readLen.value - 2))
            log.debug("unknown PDU update data type : %s"%hex(self.updateType.value))
            return String(readLen = CallableValue(readLen.value - 2))
        
        if updateData is None:
            updateData = FactoryType(UpdateDataFactory, conditional = lambda:(self.updateType.value != UpdateType.UPDATETYPE_SYNCHRONIZE))
        elif not "_UPDATE_TYPE_" in  updateData.__class__.__dict__:
            raise InvalidExpectedDataException("Try to send an invalid data update PDU")
            
        self.updateData = updateData
        
class SaveSessionInfoPDU(CompositeType):
    """
    @see: https://msdn.microsoft.com/en-us/library/cc240636.aspx
    """
    _PDUTYPE2_ = PDUType2.PDUTYPE2_SAVE_SESSION_INFO
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.infoType = UInt32Le()
        #TODO parse info data
        self.infoData = String()
        
class FastPathUpdatePDU(CompositeType):
    """
    @summary: Fast path update PDU packet
    @see: http://msdn.microsoft.com/en-us/library/cc240622.aspx
    """
    def __init__(self, updateData = None):
        CompositeType.__init__(self)
        self.updateHeader = UInt8(lambda:updateData.__class__._FASTPATH_UPDATE_TYPE_)
        self.compressionFlags = UInt8(conditional = lambda:((self.updateHeader.value >> 4) & FastPathOutputCompression.FASTPATH_OUTPUT_COMPRESSION_USED))
        self.size = UInt16Le(lambda:sizeof(self.updateData))
        
        def UpdateDataFactory():
            """
            @summary: Create correct object in accordance to self.updateHeader field
            """
            for c in [FastPathBitmapUpdateDataPDU]:
                if (self.updateHeader.value & 0xf) == c._FASTPATH_UPDATE_TYPE_:
                    return c(readLen = self.size)
            log.debug("unknown Fast Path PDU update data type : %s"%hex(self.updateHeader.value & 0xf))
            return String(readLen = self.size)
            
        if updateData is None:
            updateData = FactoryType(UpdateDataFactory)
        elif not "_FASTPATH_UPDATE_TYPE_" in  updateData.__class__.__dict__:
            raise InvalidExpectedDataException("Try to send an invalid fast path data update PDU")
            
        self.updateData = updateData
  
class BitmapUpdateDataPDU(CompositeType):
    """
    @summary: PDU use to send raw bitmap compressed or not
    @see: http://msdn.microsoft.com/en-us/library/dd306368.aspx
    """
    _UPDATE_TYPE_ = UpdateType.UPDATETYPE_BITMAP
    
    def __init__(self, readLen = None):
        """
        @param readLen: Max size of packet
        """
        CompositeType.__init__(self, readLen = readLen)
        self.numberRectangles = UInt16Le(lambda:len(self.rectangles._array))
        self.rectangles = ArrayType(BitmapData, readLen = self.numberRectangles)
        
class OrderUpdateDataPDU(CompositeType):
    """
    @summary: PDU type use to communicate Accelerated order (GDI)
    @see: http://msdn.microsoft.com/en-us/library/cc241571.aspx
    @todo: not implemented yet but need it
    """
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.pad2OctetsA = UInt16Le()
        self.numberOrders = UInt16Le(lambda:len(self.orderData._array))
        self.pad2OctetsB = UInt16Le()
        self.orderData = ArrayType(order.PrimaryDrawingOrder, readLen = self.numberOrders)

class BitmapCompressedDataHeader(CompositeType):
    """
    @summary: Compressed header of bitmap
    @see: http://msdn.microsoft.com/en-us/library/cc240644.aspx
    """
    def __init__(self, bodySize = 0, scanWidth = 0, uncompressedSize = 0, conditional = lambda:True):
        """
        @param bodySize: size of image body
        @param scanWidth: width of image
        @param uncompressedSize: size of uncompressed image
        """
        CompositeType.__init__(self, conditional = conditional)
        self.cbCompFirstRowSize = UInt16Le(0x0000, constant = True)
        #compressed data size
        self.cbCompMainBodySize = UInt16Le()
        self.cbScanWidth = UInt16Le()
        #uncompressed data size
        self.cbUncompressedSize = UInt16Le()

class BitmapData(CompositeType):
    """
    @summary: Bitmap data here the screen capture
    """
    def __init__(self, destLeft = 0, destTop = 0, destRight = 0, destBottom = 0, width = 0, height = 0, bitsPerPixel = 0, bitmapDataStream = ""):
        """
        @param destLeft: destination left coordinate
        @param destTop: destination top coordinate
        @param destRight: destination right coordinate
        @param destBottom: destination bottom coordinate
        @param width: width of image
        @param height: height of image
        @param bitsPerPixel: color depth
        @param bitmapDataStream: data
        """
        CompositeType.__init__(self)
        self.destLeft = UInt16Le(destLeft)
        self.destTop = UInt16Le(destTop)
        self.destRight = UInt16Le(destRight)
        self.destBottom = UInt16Le(destBottom)
        self.width = UInt16Le(width)
        self.height = UInt16Le(height)
        self.bitsPerPixel = UInt16Le(bitsPerPixel)
        self.flags = UInt16Le()
        self.bitmapLength = UInt16Le(lambda:(sizeof(self.bitmapComprHdr) + sizeof(self.bitmapDataStream)))
        self.bitmapComprHdr = BitmapCompressedDataHeader(bodySize = lambda:sizeof(self.bitmapDataStream), scanWidth = lambda:self.width.value, uncompressedSize = lambda:(self.width.value * self.height.value * self.bitsPerPixel.value), conditional = lambda:((self.flags.value & BitmapFlag.BITMAP_COMPRESSION) and not (self.flags.value & BitmapFlag.NO_BITMAP_COMPRESSION_HDR)))
        self.bitmapDataStream = String(bitmapDataStream, readLen = CallableValue(lambda:(self.bitmapLength.value if (not self.flags.value & BitmapFlag.BITMAP_COMPRESSION or self.flags.value & BitmapFlag.NO_BITMAP_COMPRESSION_HDR) else self.bitmapComprHdr.cbCompMainBodySize.value)))

class FastPathBitmapUpdateDataPDU(CompositeType):
    """
    @summary: Fast path version of bitmap update PDU
    @see: http://msdn.microsoft.com/en-us/library/dd306368.aspx
    """
    _FASTPATH_UPDATE_TYPE_ = FastPathUpdateType.FASTPATH_UPDATETYPE_BITMAP
    
    def __init__(self, readLen = None):
        CompositeType.__init__(self, readLen = readLen)
        self.header = UInt16Le(FastPathUpdateType.FASTPATH_UPDATETYPE_BITMAP, constant = True)
        self.numberRectangles = UInt16Le(lambda:len(self.rectangles._array))
        self.rectangles = ArrayType(BitmapData, readLen = self.numberRectangles)
    
class SlowPathInputEvent(CompositeType):
    """
    @summary: PDU use in slow-path sending client inputs
    @see: http://msdn.microsoft.com/en-us/library/cc240583.aspx
    """
    def __init__(self, messageData = None):
        CompositeType.__init__(self)
        self.eventTime = UInt32Le()
        self.messageType = UInt16Le(lambda:self.slowPathInputData.__class__._INPUT_MESSAGE_TYPE_)
        
        def SlowPathInputDataFactory():
            for c in [PointerEvent, ScancodeKeyEvent, UnicodeKeyEvent, SynchronizeEvent]:
                if self.messageType.value == c._INPUT_MESSAGE_TYPE_:
                    return c()
            raise InvalidExpectedDataException("unknown slow path input : %s"%hex(self.messageType.value))
        
        if messageData is None:
            messageData = FactoryType(SlowPathInputDataFactory)
        elif not "_INPUT_MESSAGE_TYPE_" in messageData.__class__.__dict__:
            raise InvalidExpectedDataException("try to send an invalid Slow Path Input Event")
            
        self.slowPathInputData = messageData

class SynchronizeEvent(CompositeType):
    """
    @summary: Synchronize keyboard
    @see: https://msdn.microsoft.com/en-us/library/cc240588.aspx
    """
    _INPUT_MESSAGE_TYPE_ = InputMessageType.INPUT_EVENT_SYNC
    
    def __init__(self):
        CompositeType.__init__(self)
        self.pad2Octets = UInt16Le()
        self.toggleFlags = UInt32Le()
         
class PointerEvent(CompositeType):
    """
    @summary: Event use to communicate mouse position
    @see: http://msdn.microsoft.com/en-us/library/cc240586.aspx
    """
    _INPUT_MESSAGE_TYPE_ = InputMessageType.INPUT_EVENT_MOUSE
    
    def __init__(self):
        CompositeType.__init__(self)
        self.pointerFlags = UInt16Le()
        self.xPos = UInt16Le()
        self.yPos = UInt16Le()
        
class ScancodeKeyEvent(CompositeType):
    """
    @summary: Event use to communicate keyboard informations
    @see: http://msdn.microsoft.com/en-us/library/cc240584.aspx
    """
    _INPUT_MESSAGE_TYPE_ = InputMessageType.INPUT_EVENT_SCANCODE
    
    def __init__(self):
        CompositeType.__init__(self)
        self.keyboardFlags = UInt16Le()
        self.keyCode = UInt16Le()
        self.pad2Octets = UInt16Le()
        
class UnicodeKeyEvent(CompositeType):
    """
    @summary: Event use to communicate keyboard informations
    @see: http://msdn.microsoft.com/en-us/library/cc240585.aspx
    """
    _INPUT_MESSAGE_TYPE_ = InputMessageType.INPUT_EVENT_UNICODE
    
    def __init__(self):
        CompositeType.__init__(self)
        self.keyboardFlags = UInt16Le()
        self.unicode = UInt16Le()
        self.pad2Octets = UInt16Le()