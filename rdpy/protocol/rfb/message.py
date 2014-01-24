'''
@author: sylvain
'''

from rdpy.network.type import UInt8, UInt16Be, UInt32Be, SInt32Be, String, CompositeType
from rdpy.network.const import ConstAttributes, TypeAttributes

@ConstAttributes
@TypeAttributes(String)
class ProtocolVersion(object):
    '''
    different ptotocol version
    '''
    UNKNOWN = ""
    RFB003003 = "RFB 003.003\n"
    RFB003007 = "RFB 003.007\n"
    RFB003008 = "RFB 003.008\n"

@ConstAttributes 
@TypeAttributes(UInt8)
class SecurityType(object):
    '''
    security type supported 
    (or will be supported)
    by rdpy
    '''
    INVALID = 0
    NONE = 1
    VNC = 2

@ConstAttributes
@TypeAttributes(UInt32Be)
class Pointer(object):
    '''
    mouse event code (which button)
    actually in RFB specification only$
    three buttons are supported
    '''
    BUTTON1 = 0x1
    BUTTON2 = 0x2
    BUTTON3 = 0x4

@ConstAttributes
@TypeAttributes(SInt32Be)  
class Encoding(object):
    '''
    encoding types
    '''
    RAW = 0

@ConstAttributes
@TypeAttributes(UInt8)
class ClientToServerMessages(object):
    '''
    messages types
    '''
    PIXEL_FORMAT = 0
    ENCODING = 2
    FRAME_BUFFER_UPDATE_REQUEST = 3
    KEY_EVENT = 4
    POINTER_EVENT = 5
    CUT_TEXT = 6
    
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