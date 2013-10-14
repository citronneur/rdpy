'''
Created on 12 aout 2013

@author: sylvain
'''

from rdpy.protocol.common.stream import Stream
from rdpy.protocol.common.layer import RawLayer
from types import PixelFormat,ProtocolVersion,SecurityType, Rectangle, Encoding

class Rfb(RawLayer):
    '''
    implements rfb protocol message
    '''
    CLIENT = 0
    SERVER = 1

    def __init__(self, mode):
        '''
        constructor
        mode can be only client or server mode
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
        #shared framebuffer
        self._sharedFlag = 0
        #framebuffer width
        self._width = 0
        #framebuffer height
        self._height = 0
        #pixel format structure
        self._pixelFormat = PixelFormat()
        #server name
        self._serverName = None
        #nb rectangle
        self._nbRect = 0
        #current rectangle header
        self._currentRect = Rectangle()
        #client or server adaptor
        self._observer = []
        
    def addObserver(self, observer):
        self._observer.append(observer)
    
    def expectWithHeader(self, expectedHeaderLen, callbackBody):
        '''
        2nd level of waiting event
        read expectedHeaderLen that contain body size
        '''
        self._callbackBody = callbackBody
        self.expect(expectedHeaderLen, self.expectedBody)
    
    def expectedBody(self, data):
        '''
        read header and expect body
        '''
        bodyLen = 0
        if data.len == 1:
            bodyLen = data.read_uint8()
        elif data.len == 2:
            bodyLen = data.read_beuint16()
        elif data.len == 4:
            bodyLen = data.read_beuint32()
        else:
            print "invalid header length"
            return
        self.expect(bodyLen, self._callbackBody)
        
    def readProtocolVersionFormat(self, data):
        if data.getvalue() == "RFB 003.003\n":
            self._version = ProtocolVersion.RFB003003
            return
        if data.getvalue() == "RFB 003.007\n":
            self._version = ProtocolVersion.RFB003007
            return
        if data.getvalue() == "RFB 003.008\n":
            self._version = ProtocolVersion.RFB003008
            return
        self._version = ProtocolVersion.UNKNOWN
    
    def sendProtocolVersionFormat(self):
        s = Stream()
        if self._version == ProtocolVersion.RFB003003:
            s.write("RFB 003.003\n")
        if self._version == ProtocolVersion.RFB003007:
            s.write("RFB 003.007\n")
        if self._version == ProtocolVersion.RFB003008:
            s.write("RFB 003.008\n")
        self.transport.write(s.getvalue())
        
    def connect(self):
        '''
        call when transport layer connection
        is made
        '''
        if self._mode == Rfb.CLIENT:
            self.expect(12, self.readProtocolVersion)
        else:
            self.sendProtocolVersionFormat()
    
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
        self.sendProtocolVersionFormat()
        
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
        self._version = data.read_beuint32()
        
        
    def readSecurityList(self, data):
        '''
        read all security list
        '''
        securityList = []
        while data.dataLen() > 0:
            securityList.append(data.read_uint8())
        #select high security level
        for s in securityList:
            if s in [SecurityType.NONE, SecurityType.VNC] and s > self._securityLevel:
                self._securityLevel = s
                break
        #send back security level choosen
        s = Stream()
        s.write_uint8(self._securityLevel)
        self.transport.write(s.getvalue())
        self.expect(4, self.readSecurityResult)
        
    def readSecurityResult(self, data):
        '''
        Read security result packet
        '''
        result = data.read_beuint32()
        if result == 1:
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
        self._width = data.read_beuint16()
        self._height = data.read_beuint16()
        serverPixelFomat = PixelFormat()
        serverPixelFomat.read(data)
        self.expectWithHeader(4, self.readServerName)
    
    def readServerName(self, data):
        '''
        read server name from server init packet
        '''
        self._serverName = data.getvalue()
        print "Server name %s"%self._serverName
        #end of handshake
        #send pixel format
        self.sendSetPixelFormat(self._pixelFormat)
        #write encoding
        self.sendSetEncoding()
        #request entire zone
        self.sendFramebufferUpdateRequest(False, 0, 0, self._width, self._height)
        self.expect(1, self.readServerOrder)
        
    def readServerOrder(self, data):
        '''
        read order receive from server
        '''
        packet_type = data.read_uint8()
        if packet_type == 0:
            self.expect(3, self.readFrameBufferUpdateHeader)
        
    def readFrameBufferUpdateHeader(self, data):
        '''
        read frame buffer update packet header
        '''
        #padding
        data.read_uint8()
        self._nbRect = data.read_beuint16();
        self.expect(12, self.readRectHeader)
        
    def readRectHeader(self, data):
        '''
        read rectangle header
        '''
        self._currentRect.X = data.read_beuint16()
        self._currentRect.Y = data.read_beuint16()
        self._currentRect.Width = data.read_beuint16()
        self._currentRect.Height = data.read_beuint16()
        self._currentRect.Encoding = data.read_besint32()
        
        if self._currentRect.Encoding == Encoding.RAW:
            self.expect(self._currentRect.Width * self._currentRect.Height * (self._pixelFormat.BitsPerPixel / 8), self.readRectBody)
    
    def readRectBody(self, data):
        '''
        read body of rect
        '''
        for observer in self._observer:
            observer.notifyFramebufferUpdate(self._currentRect.Width, self._currentRect.Height, self._currentRect.X, self._currentRect.Y, self._pixelFormat, self._currentRect.Encoding, data.getvalue())
        self._nbRect = self._nbRect - 1
        #if there is another rect to read
        if self._nbRect == 0:
            #job is finish send a request
            self.sendFramebufferUpdateRequest(True, 0, 0, self._width, self._height)
            self.expect(1, self.readServerOrder)
        else:
            self.expect(12, self.readRectHeader)
        
    def sendClientInit(self):
        '''
        write client init packet
        '''
        s = Stream()
        s.write_uint8(self._sharedFlag)
        self.transport.write(s.getvalue())
        self.expect(20, self.readServerInit)
        
    def sendSetPixelFormat(self, pixelFormat):
        '''
        write set pixel format packet
        '''
        s = Stream()
        #message type
        s.write_uint8(0)
        #padding
        s.write_uint8(0)
        s.write_uint8(0)
        s.write_uint8(0)
        pixelFormat.write(s)
        self.transport.write(s.getvalue())
        
    def sendSetEncoding(self):
        '''
        write set encoding packet
        '''
        s = Stream()
        #message type
        s.write_uint8(2)
        #padding
        s.write_uint8(0)
        #nb encoding
        s.write_beuint16(1)
        #raw encoding
        s.write_besint32(0)
        self.transport.write(s.getvalue())
        
    def sendFramebufferUpdateRequest(self, incremental, x, y, width, height):
        '''
        request server the specified zone
        incremental means request only change before last update
        '''
        s = Stream()
        s.write_uint8(3)
        s.write_uint8(incremental)
        s.write_beuint16(x)
        s.write_beuint16(y)
        s.write_beuint16(width)
        s.write_beuint16(height)
        self.transport.write(s.getvalue())
        
    def sendKeyEvent(self, downFlag, key):
        '''
        write key event packet
        '''
        s = Stream()
        s.write_uint8(4)
        s.write_uint8(downFlag)
        s.write_beuint16(0)
        s.write_beuint32(key)
        self.transport.write(s.getvalue())
        
    def sendPointerEvent(self, mask, x, y):
        '''
        write pointer event packet
        '''
        s= Stream()
        s.write_uint8(5)
        s.write_uint8(mask)
        s.write_beuint16(x)
        s.write_beuint16(y)
        self.transport.write(s.getvalue())
        
    def sendClientCutText(self, text):
        '''
        write client cut text event packet
        '''
        s = Stream()
        s.write_uint8(6)
        #padding
        s.write_uint8(0)
        s.write_uint8(0)
        s.write_uint8(0)
        s.write_beuint32(len(text))
        s.write(text)
        self.transport.write(s.getvalue())