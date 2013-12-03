'''
@author: sylvain
'''

from rdpy.protocol.network.layer import LayerAutomata
from rdpy.protocol.network.type import CompositeType, UInt8, UniString, UInt16Le, UInt32Le
from rdpy.utils.const import ConstAttributes, TypeAttributes

@ConstAttributes
@TypeAttributes(UInt16Le)
class SecurityFlag(object):
    SEC_INFO_PKT = 0x0040

class RDPInfo(CompositeType):
    def __init__(self):
        CompositeType.__init__(self)
        self.audioCapture = UInt8()
        self.audioPlayback = UInt8()
        self.autoLogon = UInt8()
        self.remoteApp = UInt8()
        self.consoleAudio = UInt8()
        self.compression = UInt8()
        self.domain = UniString()
        self.username = UniString()
        self.password = UniString()
        self.alternateShell = UniString()
        
class RDPExtendedInfo(CompositeType):
    def __init__(self):
        CompositeType.__init__(self)
        self.ipv6 = UInt8()
        self.adress = UniString()
        self.clientDir = UniString()
        self.performanceFlags = UInt32Le()

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
        
    def connect(self):
        self.sendInfoPkt()
        
    def sendInfoPkt(self):
        self._transport.send(self, (SecurityFlag.SEC_INFO_PKT, UInt16Le(), RDPInfo(), RDPExtendedInfo()))