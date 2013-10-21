'''
@author: sylvain
'''

from rdpy.protocol.network.type import String, UInt8, UInt16Be, UInt32Be
from rdpy.protocol.network.layer import RawLayer
from message import ServerInit, PixelFormat, FrameBufferUpdateRequest, Rectangle, KeyEvent, PointerEvent, ClientCutText
from message import ProtocolVersion, SecurityType, Encoding, ClientToServerMessages

class Rfb(RawLayer):
    '''
    implements rfb protocol
    '''
    CLIENT = 0
    SERVER = 1

    def __init__(self, mode):
        '''
        constructor
        mode can be only client or server mode
        in this RDPY version only client mode is supported
        @param mode: Rfb.CLIENT | Rfb.SERVER
        '''
        RawLayer.__init__(self)
        #usefull for rfb protocol
        self._callbackBody = None
        #mode of automata
        self._mode = mode
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
        call when transport layer connection
        is made
        '''
        if self._mode == Rfb.CLIENT:
            self.expect(12, self.readProtocolVersion)
        else:
            self.send(self._version)
        
    def readProtocolVersionFormat(self, data):
        '''
        read protocol version
        '''
        data.readType(self._version)
        if not self._version in [ProtocolVersion.RFB003003, ProtocolVersion.RFB003007, ProtocolVersion.RFB003008]:
            self._version = ProtocolVersion.UNKNOWN
    
    def readProtocolVersion(self, data):
        '''
        read handshake packet 
        protocol version nego
        '''
        self.readProtocolVersionFormat(data)
        if self._version == ProtocolVersion.UNKNOWN:
            print "Unknown protocol version %s send 003.008"%data.getvalue()
            #protocol version is unknow try best version we can handle
            self._version = ProtocolVersion.RFB003008
        #send same version of 
        self.send(self._version)
        
        #next state read security
        if self._version == ProtocolVersion.RFB003003:
            self.expect(4, self.readSecurityServer)
        else:
            self.expectWithHeader(1, self.readSecurityList)
    
    def readSecurityServer(self, data):
        '''
        security handshake for 33 rfb version
        server imposed security level
        '''
        #TODO!!!
        self._version = data.read_beuint32()
        
        
    def readSecurityList(self, data):
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
        self.expect(4, self.readSecurityResult)
        
    def readSecurityResult(self, data):
        '''
        Read security result packet
        '''
        result = UInt32Be()
        data.readType(result)
        if result == UInt32Be(1):
            print "Authentification failed"
            if self._version == ProtocolVersion.RFB003008:
                self.expectWithHeader(4, self.readSecurityFailed)
        else:
            print "Authentification OK"
            self.sendClientInit()
        
    def readSecurityFailed(self, data):
        print "Security failed cause to %s"%data.getvalue()
        
    def readServerInit(self, data):
        '''
        read server init packet
        '''
        data.readType(self._serverInit)
        self.expectWithHeader(4, self.readServerName)
    
    def readServerName(self, data):
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
        self.expect(1, self.readServerOrder)
        
    def readServerOrder(self, data):
        '''
        read order receive from server
        '''
        packet_type = UInt8()
        data.readType(packet_type)
        if packet_type == UInt8(0):
            self.expect(3, self.readFrameBufferUpdateHeader)
        
    def readFrameBufferUpdateHeader(self, data):
        '''
        read frame buffer update packet header
        '''
        #padding
        nbRect = UInt16Be()
        self._nbRect = data.readType((UInt8(), nbRect))
        self._nbRect = nbRect.value
        self.expect(12, self.readRectHeader)
        
    def readRectHeader(self, data):
        '''
        read rectangle header
        '''
        data.readType(self._currentRect)
        if self._currentRect.encoding == Encoding.RAW:
            self.expect(self._currentRect.width.value * self._currentRect.height.value * (self._pixelFormat.BitsPerPixel.value / 8), self.readRectBody)
    
    def readRectBody(self, data):
        '''
        read body of rect
        '''
        for observer in self._observer:
            observer.notifyFramebufferUpdate(self._currentRect.width, self._currentRect.height, self._currentRect.x, self._currentRect.y, self._pixelFormat, self._currentRect.encoding, data.getvalue())
        self._nbRect = self._nbRect - 1
        #if there is another rect to read
        if self._nbRect == 0:
            #job is finish send a request
            self.sendFramebufferUpdateRequest(True, 0, 0, self._serverInit.width.value, self._serverInit.height.value)
            self.expect(1, self.readServerOrder)
        else:
            self.expect(12, self.readRectHeader)
        
    def sendClientInit(self):
        '''
        write client init packet
        '''
        self.send(self._sharedFlag)
        self.expect(20, self.readServerInit)
        
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