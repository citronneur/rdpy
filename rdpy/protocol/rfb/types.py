'''
@author: sylvain
'''

from rdpy.protocol.common.network import UInt8, UInt16Be, UInt32Be, SInt32Be, String
from rdpy.protocol.common.network import CompositeType
from rdpy.utils.const import ConstAttributes

@ConstAttributes
class ProtocolVersion(object):
    '''
    different ptotocol version
    '''
    UNKNOWN = String()
    RFB003003 = String("RFB 003.003\n")
    RFB003007 = String("RFB 003.007\n")
    RFB003008 = String("RFB 003.008\n")

@ConstAttributes 
class SecurityType(object):
    '''
    security type supported 
    (or will be supported)
    by rdpy
    '''
    INVALID = UInt8(0)
    NONE = UInt8(1)
    VNC = UInt8(2)

@ConstAttributes
class Pointer(object):
    '''
    mouse event code (which button)
    actually in RFB specification only$
    three buttons are supported
    '''
    BUTTON1 = UInt32Be(0x1)
    BUTTON2 = UInt32Be(0x2)
    BUTTON3 = UInt32Be(0x4)

@ConstAttributes  
class Encoding(object):
    '''
    encoding types
    '''
    RAW = SInt32Be(0)
    
class PixelFormat(CompositeType):
    '''
    pixel format structure
    '''
    def __init__(self):
        CompositeType.__init__(self)
        self.BitsPerPixel = UInt8(32)
        self.Depth = UInt8(24)
        self.BigEndianFlag = UInt8(False)
        self.TrueColorFlag = UInt8(True)
        self.RedMax = UInt16Be(255)
        self.GreenMax = UInt16Be(255)
        self.BlueMax = UInt16Be(255)
        self.RedShift = UInt8(16)
        self.GreenShift = UInt8(8)
        self.BlueShift = UInt8(0)
        self.padding1 = UInt16Be()
        self.padding2 = UInt8()
        
class PixelFormatMessage(CompositeType):
    '''
    message structure used in rfb
    to send pixel format structure
    '''
    def __init__(self, pixelFormat):
        CompositeType.__init__(self)
        self.type = UInt8(0)
        self.padding1 = UInt16Be()
        self.padding2 = UInt8()
        self.pixelFormat = pixelFormat
        
class SetEncodingMessage(CompositeType):
    '''
    message structure used in rfb
    to send set encoding
    Actually basic message that only send
    raw encoding
    '''
    def __init__(self):
        self.type = UInt8(2)
        self.padding = UInt8()
        self.nbEncoding = UInt16Be(1)
        self.raw = Encoding.RAW
    
        
class ServerInit(CompositeType):
    '''
    message send by server to indicate
    framebuffer configuration
    '''
    def __init__(self):
        CompositeType.__init__(self)
        self.width = UInt16Be()
        self.height = UInt16Be()
        self.pixelFormat = PixelFormat()

    
class Rectangle(object):
    def __init__(self):
        self.X = 0
        self.Y = 0
        self.Width = 0
        self.Height = 0
        self.Encoding = 0