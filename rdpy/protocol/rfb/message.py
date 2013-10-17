'''
@author: sylvain
'''

from rdpy.protocol.network.type import UInt8, UInt16Be, UInt32Be, SInt32Be, String, CompositeType
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

@ConstAttributes
class ClientToServerMessages(object):
    '''
    messages types
    '''
    PIXEL_FORMAT = UInt8(0)
    ENCODING = UInt8(2)
    FRAME_BUFFER_UPDATE_REQUEST = UInt8(3)
    KEY_EVENT = UInt8(4)
    POINTER_EVENT = UInt8(5)
    CUT_TEXT = UInt8(6)
    
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
        self.padding = (UInt16Be(), UInt8())
    
        
class ServerInit(CompositeType):
    '''
    server init structure
    framebuffer configuration
    '''
    def __init__(self):
        CompositeType.__init__(self)
        self.width = UInt16Be()
        self.height = UInt16Be()
        self.pixelFormat = PixelFormat()
        
class FrameBufferUpdateRequest(CompositeType):
    '''
    fb update request send from client to server
    '''
    def __init__(self, incremental = False, x = 0, y = 0, width = 0, height = 0):
        CompositeType.__init__(self)
        self.incremental = UInt8(incremental)
        self.x = UInt16Be(x)
        self.y = UInt16Be(y)
        self.width = UInt16Be(width)
        self.height = UInt16Be(height)

    
class Rectangle(CompositeType):
    '''
    header message of update rect
    '''
    def __init__(self):
        CompositeType.__init__(self)
        self.x = UInt16Be()
        self.y = UInt16Be()
        self.width = UInt16Be()
        self.height = UInt16Be()
        self.encoding = SInt32Be()
        
class KeyEvent(CompositeType):
    '''
    key event structure message
    '''
    def __init__(self, downFlag = False, key = 0):
        CompositeType.__init__(self)
        self.downFlag = UInt8(downFlag)
        self.padding = UInt16Be()
        self.key = UInt32Be(key)
        
class PointerEvent(CompositeType):
    '''
    pointer event structure message
    '''
    def __init__(self, mask = 0, x = 0, y = 0):
        CompositeType.__init__(self)
        self.mask = UInt8(mask)
        self.x = UInt16Be(x)
        self.y = UInt16Be(y)
        
class ClientCutText(CompositeType):
    '''
    client cut text message message
    '''
    def __init__(self, text = ""):
        CompositeType.__init__(self)
        self.padding = (UInt16Be(), UInt8())
        self.size = UInt32Be(len(text))
        self.message = String(text)