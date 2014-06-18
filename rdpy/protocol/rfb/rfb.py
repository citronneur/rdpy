'''
@author: citronneur
'''
from twisted.internet import protocol
from rdpy.network.layer import RawLayer, LayerMode
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

class Rfb(RawLayer):
    '''
    implements rfb protocol
    '''

    def __init__(self, mode):
        '''
        constructor
        '''
        RawLayer.__init__(self, mode)
        #usefull for rfb protocol
        self._callbackBody = None
        #protocol version negociated
        self._version = ProtocolVersion.RFB003008
        #nb security launch by server
        self._securityLevel = SecurityType.INVALID
        #shared framebuffer client init message
        self._sharedFlag = UInt8(False)
        #server init message
        #which contain framebuffer dim and pixel format
        self._serverInit = ServerInit()
        #client pixel format
        self._pixelFormat = PixelFormat()
        #server name
        self._serverName = String()
        #nb rectangle
        self._nbRect = 0
        #current rectangle header
        self._currentRect = Rectangle()
        #client or server adaptor
        self._observer = []
        
    def addObserver(self, observer):
        '''
        add observer for input/ouput events
        @param observer: RfbObserver interface implementation
        '''
        self._observer.append(observer)
    
    def expectWithHeader(self, expectedHeaderLen, callbackBody):
        '''
        2nd level of waiting event
        read expectedHeaderLen that contain body size
        @param expectedHeaderLen: bytes read and use to compute bodylen
        @param callbackBody: next state use when value read from header 
        are received
        '''
        self._callbackBody = callbackBody
        self.expect(expectedHeaderLen, self.expectedBody)
    
    def expectedBody(self, data):
        '''
        read header and wait header value to call next state
        @param data: Stream that length are to header length (1|2|4 bytes)
        set next state to callBack body when length read from header
        are received
        '''
        bodyLen = None
        if data.len == 1:
            bodyLen = UInt8()
        elif data.len == 2:
            bodyLen = UInt16Be()
        elif data.len == 4:
            bodyLen = UInt32Be()
        else:
            print "invalid header length"
            return
        data.readType(bodyLen)
        self.expect(bodyLen.value, self._callbackBody)
        
    def connect(self):
        '''
        call when transport layer connection is made
        in Client mode -> wait protocol version
        in Server mode -> send protocol version
        '''
        if self._mode == LayerMode.CLIENT:
            self.expect(12, self.recvProtocolVersion)
        else:
            self.send(self._version)
        
    def readProtocolVersion(self, data):
        '''
        read protocol version and set
        self._version var member
        @param data: Stream may contain protocol version string (ProtocolVersion)
        '''
        data.readType(self._version)
        if not self._version in [ProtocolVersion.RFB003003, ProtocolVersion.RFB003007, ProtocolVersion.RFB003008]:
            self._version = ProtocolVersion.UNKNOWN
    
    def recvProtocolVersion(self, data):
        '''
        read handshake packet 
        protocol version nego
        if protocol receive from client is unknow
        try best version of protocol version (ProtocolVersion.RFB003008)
        @param data: Stream
        '''
        self.readProtocolVersion(data)
        if self._version == ProtocolVersion.UNKNOWN:
            print "Unknown protocol version %s send 003.008"%data.getvalue()
            #protocol version is unknow try best version we can handle
            self._version = ProtocolVersion.RFB003008
        #send same version of 
        self.send(self._version)
        
        #next state read security
        if self._version == ProtocolVersion.RFB003003:
            self.expect(4, self.recvSecurityServer)
        else:
            self.expectWithHeader(1, self.recvSecurityList)
    
    def recvSecurityServer(self, data):
        '''
        security handshake for 33 rfb version
        server imposed security level
        '''
        #TODO!!!
        
    def recvSecurityList(self, data):
        '''
        read all security list
        '''
        securityList = []
        while data.dataLen() > 0:
            securityElement = UInt8()
            data.readType(securityElement)
            securityList.append(securityElement)
        #select high security level
        for s in securityList:
            if s in [SecurityType.NONE, SecurityType.VNC] and s > self._securityLevel:
                self._securityLevel = s
                break
        #send back security level choosen
        self.send(self._securityLevel)
        self.expect(4, self.recvSecurityResult)
        
    def recvSecurityResult(self, data):
        '''
        Read security result packet
        '''
        result = UInt32Be()
        data.readType(result)
        if result == UInt32Be(1):
            print "Authentification failed"
            if self._version == ProtocolVersion.RFB003008:
                self.expectWithHeader(4, self.recvSecurityFailed)
        else:
            print "Authentification OK"
            self.sendClientInit()
        
    def recvSecurityFailed(self, data):
        print "Security failed cause to %s"%data.getvalue()
        
    def recvServerInit(self, data):
        '''
        read server init packet
        '''
        data.readType(self._serverInit)
        self.expectWithHeader(4, self.recvServerName)
    
    def recvServerName(self, data):
        '''
        read server name from server init packet
        '''
        data.readType(self._serverName)
        print "Server name %s"%str(self._serverName)
        #end of handshake
        #send pixel format
        self.sendPixelFormat(self._pixelFormat)
        #write encoding
        self.sendSetEncoding()
        #request entire zone
        self.sendFramebufferUpdateRequest(False, 0, 0, self._serverInit.width.value, self._serverInit.height.value)
        self.expect(1, self.recvServerOrder)
        
    def recvServerOrder(self, data):
        '''
        read order receive from server
        '''
        packet_type = UInt8()
        data.readType(packet_type)
        if packet_type == UInt8(0):
            self.expect(3, self.recvFrameBufferUpdateHeader)
        
    def recvFrameBufferUpdateHeader(self, data):
        '''
        read frame buffer update packet header
        '''
        #padding
        nbRect = UInt16Be()
        self._nbRect = data.readType((UInt8(), nbRect))
        self._nbRect = nbRect.value
        self.expect(12, self.recvRectHeader)
        
    def recvRectHeader(self, data):
        '''
        read rectangle header
        '''
        data.readType(self._currentRect)
        if self._currentRect.encoding == Encoding.RAW:
            self.expect(self._currentRect.width.value * self._currentRect.height.value * (self._pixelFormat.BitsPerPixel.value / 8), self.recvRectBody)
    
    def recvRectBody(self, data):
        '''
        read body of rect
        '''
        for observer in self._observer:
            observer.notifyFramebufferUpdate(self._currentRect.width.value, self._currentRect.height.value, self._currentRect.x.value, self._currentRect.y.value, self._pixelFormat, self._currentRect.encoding, data.getvalue())
            
        self._nbRect = self._nbRect - 1
        #if there is another rect to read
        if self._nbRect == 0:
            #job is finish send a request
            self.sendFramebufferUpdateRequest(True, 0, 0, self._serverInit.width.value, self._serverInit.height.value)
            self.expect(1, self.recvServerOrder)
        else:
            self.expect(12, self.recvRectHeader)
        
    def sendClientInit(self):
        '''
        write client init packet
        '''
        self.send(self._sharedFlag)
        self.expect(20, self.recvServerInit)
        
    def sendPixelFormat(self, pixelFormat):
        '''
        send pixel format structure
        '''
        self.send((ClientToServerMessages.PIXEL_FORMAT, UInt16Be(), UInt8(), pixelFormat))
        
    def sendSetEncoding(self):
        '''
        send set encoding packet
        '''
        self.send((ClientToServerMessages.ENCODING, UInt8(), UInt16Be(1), Encoding.RAW))
        
    def sendFramebufferUpdateRequest(self, incremental, x, y, width, height):
        '''
        request server the specified zone
        incremental means request only change before last update
        '''
        self.send((ClientToServerMessages.FRAME_BUFFER_UPDATE_REQUEST, FrameBufferUpdateRequest(incremental, x, y, width, height)))
        
    def sendKeyEvent(self, downFlag, key):
        '''
        write key event packet
        '''
        self.send((ClientToServerMessages.KEY_EVENT, KeyEvent(downFlag, key)))
        
    def sendPointerEvent(self, mask, x, y):
        '''
        write pointer event packet
        '''
        self.send((ClientToServerMessages.POINTER_EVENT, PointerEvent(mask, x, y)))
        
    def sendClientCutText(self, text):
        '''
        write client cut text event packet
        '''
        self.send((ClientToServerMessages.CUT_TEXT, ClientCutText(text)))

class ClientFactory(protocol.Factory):
    '''
    Factory of RFB protocol
    '''
    def __init__(self, observer):
        '''
        save mode and adapter
        @param adapter: graphic client adapter
        '''
        self._observer = observer
    
    def buildProtocol(self, addr):
        '''
        function call by twisted on connection
        @param addr: adresse where client try to connect
        '''
        protocol =  Rfb(LayerMode.CLIENT)
        protocol.addObserver(self._observer)
        self._observer.setProtocol(protocol)
        return protocol
    
    def startedConnecting(self, connector):
        print 'Started to connect.'
        
    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        
class RfbObserver(object):
    '''
    Rfb protocol obserser
    '''
    def notifyFramebufferUpdate(self, width, height, x, y, pixelFormat, encoding, data):
        '''
        recv framebuffer update
        @param width : width of image
        @param height : height of image
        @param x : x position
        @param y : y position
        @param pixelFormat : pixel format struct from rfb.types
        @param encoding : encoding struct from rfb.types
        @param data : in respect of dataFormat and pixelFormat
        '''
        pass
    
    def setProtocol(self, rfbLayer):
        '''
        call when observer is added to an rfb layer
        @param: rfbLayer layer inform the observer
        '''
        pass