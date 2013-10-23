'''
@author sylvain
@summary gcc language
@contact: http://msdn.microsoft.com/en-us/library/cc240510.aspx
'''
from rdpy.utils.const import ConstAttributes
from rdpy.protocol.network.type import *
import per

t124_02_98_oid = ( 0, 0, 20, 124, 0, 1 )
h221_cs_key = "Duca";
h221_sc_key = "McDn";

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
    
@ConstAttributes
class HighColor(object):
    '''
    high color of client
    '''
    HIGH_COLOR_4BPP = UInt16Le(0x0004)
    HIGH_COLOR_8BPP = UInt16Le(0x0008)
    HIGH_COLOR_15BPP = UInt16Le(0x000f)
    HIGH_COLOR_16BPP = UInt16Le(0x0010)
    HIGH_COLOR_24BPP = UInt16Le(0x0018)

@ConstAttributes
class Support(object):
    '''
    support depth flag
    '''
    RNS_UD_24BPP_SUPPORT = UInt16Le(0x0001)
    RNS_UD_16BPP_SUPPORT = UInt16Le(0x0002)
    RNS_UD_15BPP_SUPPORT = UInt16Le(0x0004)
    RNS_UD_32BPP_SUPPORT = UInt16Le(0x0008)

@ConstAttributes
class CapabilityFlags(object):
    '''
    @contact: http://msdn.microsoft.com/en-us/library/cc240510.aspx
    for more details on each flags click above
    '''
    RNS_UD_CS_SUPPORT_ERRINFO_PDU = UInt16Le(0x0001)
    RNS_UD_CS_WANT_32BPP_SESSION = UInt16Le(0x0002)
    RNS_UD_CS_SUPPORT_STATUSINFO_PDU = UInt16Le(0x0004)
    RNS_UD_CS_STRONG_ASYMMETRIC_KEYS = UInt16Le(0x0008)
    RN_UD_CS_UNUSED = UInt16Le(0x0010)
    RNS_UD_CS_VALID_CONNECTION_TYPE = UInt16Le(0x0020)
    RNS_UD_CS_SUPPORT_MONITOR_LAYOUT_PDU = UInt16Le(0x0040)
    RNS_UD_CS_SUPPORT_NETCHAR_AUTODETECT = UInt16Le(0x0080)
    RNS_UD_CS_SUPPORT_DYNVC_GFX_PROTOCOL = UInt16Le(0x0100)
    RNS_UD_CS_SUPPORT_DYNAMIC_TIME_ZONE = UInt16Le(0x0200)
    RNS_UD_CS_SUPPORT_HEARTBEAT_PDU = UInt16Le(0x0400)

@ConstAttributes 
class ConnectionType(object):
    '''
    this information is correct if 
    RNS_UD_CS_VALID_CONNECTION_TYPE flag is set on capabilityFlag
    @contact: http://msdn.microsoft.com/en-us/library/cc240510.aspx
    '''
    CONNECTION_TYPE_MODEM = UInt8(0x01)
    CONNECTION_TYPE_BROADBAND_LOW = UInt8(0x02)
    CONNECTION_TYPE_SATELLITE = UInt8(0x03)
    CONNECTION_TYPE_BROADBAND_HIGH = UInt8(0x04)
    CONNECTION_TYPE_WAN = UInt8(0x05)
    CONNECTION_TYPE_LAN = UInt8(0x06)
    CONNECTION_TYPE_AUTODETECT = UInt8(0x07)

@ConstAttributes
class Version(object):
    '''
    supported version of RDP
    '''
    RDP_VERSION_4 = UInt32Le(0x00080001)
    RDP_VERSION_5_PLUS = UInt32Le(0x00080004)

@ConstAttributes
class Sequence(object):
    RNS_UD_SAS_DEL = UInt16Le(0xAA03)
    
@ConstAttributes   
class Encryption(object):
    '''
    encryption method supported
    @deprecated: because rdpy use ssl but need to send to server...
    '''
    ENCRYPTION_FLAG_40BIT = UInt32Le(0x00000001)
    ENCRYPTION_FLAG_128BIT = UInt32Le(0x00000002)
    ENCRYPTION_FLAG_56BIT = UInt32Le(0x00000008)
    FIPS_ENCRYPTION_FLAG = UInt32Le(0x00000010)


class ClientCoreSettings(CompositeType):
    '''
    class that represent core setting of client
    '''
    def __init__(self):
        CompositeType.__init__(self)
        self.rdpVersion = Version.RDP_VERSION_5_PLUS
        self.desktopWidth = UInt16Le(1280)
        self.desktopHeight = UInt16Le(1024)
        self.colorDepth = ColorDepth.RNS_UD_COLOR_8BPP
        self.sasSequence = Sequence.RNS_UD_SAS_DEL
        self.kbdLayout = UInt32Le(0x409)
        self.clientBuild = UInt32Le(3790)
        self.clientName = UniString("rdpy" + "\x00"*11)
        self.keyboardType = UInt32Le(4)
        self.keyboardSubType = UInt32Le(0)
        self.keyboardFnKeys = UInt32Le(12)
        self.imeFileName = String("\x00"*64)
        self.postBeta2ColorDepth = ColorDepth.RNS_UD_COLOR_8BPP
        self.clientProductId = UInt16Le(1)
        self.serialNumber = UInt32Le(0)
        self.highColorDepth = HighColor.HIGH_COLOR_24BPP
        self.supportedColorDepths = Support.RNS_UD_24BPP_SUPPORT | Support.RNS_UD_16BPP_SUPPORT | Support.RNS_UD_15BPP_SUPPORT
        self.earlyCapabilityFlags = CapabilityFlags.RNS_UD_CS_SUPPORT_ERRINFO_PDU
        self.clientDigProductId = String("\x00"*64)
        self.connectionType = UInt8()
        self.pad1octet = UInt8()
        self.serverSelectedProtocol = UInt32Le()
    
class ServerCoreSettings(CompositeType):
    '''
    server side core settings structure
    '''
    def __init__(self):
        CompositeType.__init__(self)
        self.rdpVersion = Version.RDP_VERSION_5_PLUS
        
class ClientSecuritySettings(CompositeType):
    '''
    client security setting
    @deprecated: because we use ssl
    '''
    def __init__(self):
        CompositeType.__init__(self)
        self.encryptionMethods = UInt32Le()
        self.extEncryptionMethods = UInt32Le()

class Channel(object):
    '''
    channels structure share between
    client and server
    '''
    def __init__(self):
        #name of channel
        self.name = ""
        #unknown
        self.options = 0
        #id of channel
        self.channelId = 0
        #True if channel is connect
        self.connect = False
        
class ClientSettings(object):
    '''
    class which group all client settings supported by RDPY
    '''
    def __init__(self):
        self.core = ClientCoreSettings()
        #list of Channel read network gcc packet
        self.networkChannels = []
        self.security = ClientSecuritySettings()
        
def writeConferenceCreateRequest(settings):
    '''
    write conference create request structure
    @param settings: ClientSettings
    @return: struct that represent
    '''
    userData = writeClientDataBlocks(settings)
    userDataStream = Stream()
    userDataStream.writeType(userData)
    
    return (per.writeChoice(0), per.writeObjectIdentifier(t124_02_98_oid),
            per.writeLength(len(userDataStream.getvalue()) + 14), per.writeChoice(0),
            per.writeSelection(0x08), per.writeNumericString("1", 1), per.writePadding(1),
            per.writeNumberOfSet(1), per.writeChoice(0xc0),
            per.writeOctetStream(h221_cs_key, 4), per.writeOctetStream(userDataStream.getvalue()))
    
    
def writeClientDataBlocks(settings):
    '''
    write all blocks for client
    and return gcc valid structure
    @param settings: ClientSettings
    '''
    return (writeClientCoreData(settings.core), 
            writeClientNetworkData(settings.networkChannels),
            writeClientSecurityData(settings.security))

def writeClientCoreData(core):
    '''
    write client settings in GCC language
    @param settings: ClientSettings structure
    @return: structure that represent client data blocks
    '''
    return (ClientToServerMessage.CS_CORE, UInt16Le(sizeof(core) + 4), core)

def writeClientSecurityData(security):
    '''
    write security header block and security structure
    @param security: ClientSecuritySettings
    @return: gcc client security data
    '''
    return (ClientToServerMessage.CS_SECURITY, UInt16Le(sizeof(security) + 4), security)

def writeClientNetworkData(channels):
    '''
    write network packet whith channels infos
    @param channels: list of Channel
    @return: gcc network packet
    '''
    if len(channels) == 0:
        return ()
    result = []
    result.append(UInt32Le(len(channels)))
    for channel in channels:
        result.append((String(channel.name[0:8] + "\x00" * (8 - len(channel.name))), UInt32Le(channel.options)))
    
    resultPacket = tuple(result)
    return (ClientToServerMessage.CS_NET, UInt16Le(sizeof(resultPacket) + 4), resultPacket)
    