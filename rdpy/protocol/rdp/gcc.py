'''
@author sylvain
@summary gcc language
'''
#constants declaration
#server data
SC_CORE =           0x0C01
SC_SECURITY =       0x0C02
SC_NET =            0x0C03

#client data
CS_CORE =           0xC001
CS_SECURITY =       0xC002
CS_NET =            0xC003
CS_CLUSTER =        0xC004
CS_MONITOR =        0xC005

#depth color
RNS_UD_COLOR_8BPP =         0xCA01
RNS_UD_COLOR_16BPP_555 =    0xCA02
RNS_UD_COLOR_16BPP_565 =    0xCA03
RNS_UD_COLOR_24BPP =        0xCA04

RNS_UD_24BPP_SUPPORT =      0x0001
RNS_UD_16BPP_SUPPORT =      0x0002
RNS_UD_15BPP_SUPPORT =      0x0004
RNS_UD_32BPP_SUPPORT =      0x0008

RNS_UD_SAS_DEL =            0xAA03

#rdp version
RDP_VERSION_4 =             0x00080001
RDP_VERSION_5_PLUS =        0x00080004

RNS_UD_CS_SUPPORT_ERRINFO_PDU =       0x0001

class ClientCoreSettings:
    '''
    class that represent core setting of client
    '''
    rdpVersion = RDP_VERSION_5_PLUS
    desktopWidth = 800
    desktopHeight = 600
    kbdLayout = 0x409
    clientBuild = 2100
    clientName = "rdpy"
    keyboardType = 4
    keyboardSubType = 0
    keyboardFnKeys = 12
    postBeta2ColorDepth = RNS_UD_COLOR_24BPP
    
class ServerCoreSettings:
    '''
    server side core settings structure
    '''
    rdpVersion = RDP_VERSION_5_PLUS