#
# Copyright (c) 2014 Sylvain Peyrefitte
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
Implement Remote FrameBuffer protocol use in VNC client and server
@see: http://www.realvnc.com/docs/rfbproto.pdf

@todo: server side of protocol
@todo: vnc security type
@todo: more encoding rectangle
"""

from twisted.internet import protocol
from rdpy.network.layer import RawLayer
from rdpy.network.type import UInt8, UInt16Be, UInt32Be, SInt32Be, String, CompositeType
from rdpy.base.error import InvalidValue, CallPureVirtualFuntion

class ProtocolVersion(object):
    """
    Different protocol version
    """
    UNKNOWN = ""
    RFB003003 = "RFB 003.003\n"
    RFB003007 = "RFB 003.007\n"
    RFB003008 = "RFB 003.008\n"

class SecurityType(object):
    """
    Security type supported 
    """
    INVALID = 0
    NONE = 1
    VNC = 2

class Pointer(object):
    """
    Mouse event code (which button)
    actually in RFB specification only
    three buttons are supported
    """
    BUTTON1 = 0x1
    BUTTON2 = 0x2
    BUTTON3 = 0x4
  
class Encoding(object):
    """
    Encoding types of FrameBuffer update
    """
    RAW = 0

class ClientToServerMessages(object):
    """
    Client to server messages types
    """
    PIXEL_FORMAT = 0
    ENCODING = 2
    FRAME_BUFFER_UPDATE_REQUEST = 3
    KEY_EVENT = 4
    POINTER_EVENT = 5
    CUT_TEXT = 6
    
class PixelFormat(CompositeType):
    """
    Pixel format structure
    """
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
    """
    Server init structure
    FrameBuffer configuration
    """
    def __init__(self):
        CompositeType.__init__(self)
        self.width = UInt16Be()
        self.height = UInt16Be()
        self.pixelFormat = PixelFormat()
        
class FrameBufferUpdateRequest(CompositeType):
    """
    FrameBuffer update request send from client to server
    Incremental means that server send update with a specific
    order, and client must draw orders in same order
    """
    def __init__(self, incremental = False, x = 0, y = 0, width = 0, height = 0):
        CompositeType.__init__(self)
        self.incremental = UInt8(incremental)
        self.x = UInt16Be(x)
        self.y = UInt16Be(y)
        self.width = UInt16Be(width)
        self.height = UInt16Be(height)

    
class Rectangle(CompositeType):
    """
    Header message of update rectangle
    """
    def __init__(self):
        CompositeType.__init__(self)
        self.x = UInt16Be()
        self.y = UInt16Be()
        self.width = UInt16Be()
        self.height = UInt16Be()
        self.encoding = SInt32Be()
        
class KeyEvent(CompositeType):
    """
    Key event structure message
    Use to send a keyboard event
    """
    def __init__(self):
        CompositeType.__init__(self)
        self.downFlag = UInt8(False)
        self.padding = UInt16Be()
        self.key = UInt32Be()
        
class PointerEvent(CompositeType):
    """
    Pointer event structure message
    Use to send mouse event
    """
    def __init__(self):
        CompositeType.__init__(self)
        self.mask = UInt8()
        self.x = UInt16Be()
        self.y = UInt16Be()
        
class ClientCutText(CompositeType):
    """
    Client cut text message message
    Use to simulate copy paste (ctrl-c ctrl-v) only for text
    """
    def __init__(self, text = ""):
        CompositeType.__init__(self)
        self.padding = (UInt16Be(), UInt8())
        self.size = UInt32Be(len(text))
        self.message = String(text)

class RFB(RawLayer):
    """
    Implement RFB protocol
    """
    def __init__(self, listener):
        """
        @param listener: listener use to inform new orders
        """
        RawLayer.__init__(self)
        #set client listener
        self._clientListener = listener
        #useful for RFB protocol
        self._callbackBody = None
        #protocol version negotiated
        self._version = String(ProtocolVersion.RFB003008)
        #number security launch by server
        self._securityLevel = UInt8(SecurityType.INVALID)
        #shared FrameBuffer client init message
        self._sharedFlag = UInt8(False)
        #server init message
        #which contain FrameBuffer dim and pixel format
        self._serverInit = ServerInit()
        #client pixel format
        self._pixelFormat = PixelFormat()
        #server name
        self._serverName = String()
        #nb rectangle
        self._nbRect = 0
        #current rectangle header
        self._currentRect = Rectangle()
        #ready to send events
        self._ready = False
    
    def expectWithHeader(self, expectedHeaderLen, callbackBody):
        """
        2nd level of waiting event
        read expectedHeaderLen that contain body size
        @param expectedHeaderLen: contains the number of bytes, which body length needs to be encoded
        @param callbackBody: next state use when expected date from expectedHeaderLen
        are received
        """
        self._callbackBody = callbackBody
        self.expect(expectedHeaderLen, self.expectedBody)
    
    def expectedBody(self, data):
        """
        Read header and wait header value to call next state
        @param data: Stream that length are to header length (1|2|4 bytes)
        set next state to callBack body when length read from header
        are received
        """
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
        """
        Call when transport layer connection is made
        in Client mode -> wait protocol version
        """
        self.expect(12, self.recvProtocolVersion)
        
    def readProtocolVersion(self, data):
        """
        Read protocol version
        @param data: Stream may contain protocol version string (ProtocolVersion)
        """
        data.readType(self._version)
        if not self._version.value in [ProtocolVersion.RFB003003, ProtocolVersion.RFB003007, ProtocolVersion.RFB003008]:
            self._version.value = ProtocolVersion.UNKNOWN
    
    def recvProtocolVersion(self, data):
        """
        Read handshake packet 
        If protocol receive from client is unknown
        try best version of protocol version (ProtocolVersion.RFB003008)
        @param data: Stream
        """
        self.readProtocolVersion(data)
        if self._version.value == ProtocolVersion.UNKNOWN:
            print "Unknown protocol version %s send 003.008"%data.getvalue()
            #protocol version is unknown try best version we can handle
            self._version.value = ProtocolVersion.RFB003008
        #send same version of 
        self.send(self._version)
        
        #next state read security
        if self._version.value == ProtocolVersion.RFB003003:
            self.expect(4, self.recvSecurityServer)
        else:
            self.expectWithHeader(1, self.recvSecurityList)
    
    def recvSecurityServer(self, data):
        """
        Security handshake for 33 RFB version
        Server imposed security level
        @param data: well formed packet
        """
        #TODO!!!
        pass
        
    def recvSecurityList(self, data):
        """
        Read security list packet send from server to client
        @param data: Stream that contains well formed packet
        """
        securityList = []
        while data.dataLen() > 0:
            securityElement = UInt8()
            data.readType(securityElement)
            securityList.append(securityElement)
        #select high security level
        for s in securityList:
            if s.value in [SecurityType.NONE, SecurityType.VNC] and s > self._securityLevel:
                self._securityLevel = s
                break
        #send back security level choosen
        self.send(self._securityLevel)
        self.expect(4, self.recvSecurityResult)
        
    def recvSecurityResult(self, data):
        """
        Read security result packet
        Use by server to inform connection status of client
        @param data: Stream that contain well formed packet 
        """
        result = UInt32Be()
        data.readType(result)
        if result == UInt32Be(1):
            print "Authentification failed"
            if self._version.value == ProtocolVersion.RFB003008:
                self.expectWithHeader(4, self.recvSecurityFailed)
        else:
            print "Authentification OK"
            self.sendClientInit()
        
    def recvSecurityFailed(self, data):
        """
        Send by server to inform reason of why it's refused client
        @param data: Stream that contains well formed packet
        """
        print "Security failed cause to %s"%data.getvalue()
        
    def recvServerInit(self, data):
        """
        Read server init packet
        @param data: Stream that contains well formed packet
        """
        data.readType(self._serverInit)
        self.expectWithHeader(4, self.recvServerName)
    
    def recvServerName(self, data):
        """
        Read server name
        @param data: Stream that contains well formed packet
        """
        data.readType(self._serverName)
        print "Server name %s"%str(self._serverName)
        #end of handshake
        #send pixel format
        self.sendPixelFormat(self._pixelFormat)
        #write encoding
        self.sendSetEncoding()
        #request entire zone
        self.sendFramebufferUpdateRequest(False, 0, 0, self._serverInit.width.value, self._serverInit.height.value)
        #now i'm ready to send event
        self._ready = True;
        
        self.expect(1, self.recvServerOrder)
        
    def recvServerOrder(self, data):
        """
        Read order receive from server
        Main function for bitmap update from server to client
        @param data: Stream that contains well formed packet
        """
        packet_type = UInt8()
        data.readType(packet_type)
        if packet_type == UInt8(0):
            self.expect(3, self.recvFrameBufferUpdateHeader)
        
    def recvFrameBufferUpdateHeader(self, data):
        """
        Read frame buffer update packet header
        @param data: Stream that contains well formed packet
        """
        #padding
        nbRect = UInt16Be()
        self._nbRect = data.readType((UInt8(), nbRect))
        self._nbRect = nbRect.value
        self.expect(12, self.recvRectHeader)
        
    def recvRectHeader(self, data):
        """
        Read rectangle header
        @param data: Stream that contains well formed packet
        """
        data.readType(self._currentRect)
        if self._currentRect.encoding.value == Encoding.RAW:
            self.expect(self._currentRect.width.value * self._currentRect.height.value * (self._pixelFormat.BitsPerPixel.value / 8), self.recvRectBody)
    
    def recvRectBody(self, data):
        """
        Read body of rectangle update
        @param data: Stream that contains well formed packet
        """
        self._clientListener.recvRectangle(self._currentRect, self._pixelFormat, data.getvalue())
           
        self._nbRect = self._nbRect - 1
        #if there is another rect to read
        if self._nbRect == 0:
            #job is finish send a request
            self.sendFramebufferUpdateRequest(True, 0, 0, self._serverInit.width.value, self._serverInit.height.value)
            self.expect(1, self.recvServerOrder)
        else:
            self.expect(12, self.recvRectHeader)
        
    def sendClientInit(self):
        """
        Send client init packet
        """
        self.send(self._sharedFlag)
        self.expect(20, self.recvServerInit)
        
    def sendPixelFormat(self, pixelFormat):
        """
        Send pixel format structure
        Very important packet that inform the image struct supported by the client
        @param pixelFormat: PixelFormat struct
        """
        self.send((UInt8(ClientToServerMessages.PIXEL_FORMAT), UInt16Be(), UInt8(), pixelFormat))
        
    def sendSetEncoding(self):
        """
        Send set encoding packet
        Actually only RAW bitmap encoding are used
        """
        self.send((UInt8(ClientToServerMessages.ENCODING), UInt8(), UInt16Be(1), SInt32Be(Encoding.RAW)))
        
    def sendFramebufferUpdateRequest(self, incremental, x, y, width, height):
        """
        Request server the specified zone
        incremental means request only change before last update
        """
        self.send((UInt8(ClientToServerMessages.FRAME_BUFFER_UPDATE_REQUEST), FrameBufferUpdateRequest(incremental, x, y, width, height)))
        
    def sendKeyEvent(self, keyEvent):
        """
        Write key event packet
        @param keyEvent: KeyEvent struct to send
        """
        self.send((UInt8(ClientToServerMessages.KEY_EVENT), keyEvent))
        
    def sendPointerEvent(self, pointerEvent):
        """
        Write pointer event packet
        @param pointerEvent: PointerEvent struct use
        """
        self.send((UInt8(ClientToServerMessages.POINTER_EVENT), pointerEvent))
        
    def sendClientCutText(self, text):
        """
        write client cut text event packet
        """
        self.send((UInt8(ClientToServerMessages.CUT_TEXT), ClientCutText(text)))
        
class RFBClientListener(object):
    """
    Interface use to expose event receive from RFB layer
    """
    def recvRectangle(self, rectangle, pixelFormat, data):
        """
        Receive rectangle order
        Main update order type
        @param rectangle: Rectangle type header of packet
        @param pixelFormat: pixelFormat struct of current session
        @param data: image data
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "recvRectangle", "RFBListener"))
    
        
class RFBController(RFBClientListener):
    """
    Class use to manage RFB order and dispatch throw observers
    """
    def __init__(self, mode):
        """
        @param mode: mode of inner RFB layer
        """
        self._clientObservers = []
        #rfb layer to send client orders
        self._rfbLayer = RFB(self)
        
    def getRFBLayer(self):
        """
        @return: RFB layer build by controller
        """
        return self._rfbLayer
        
    def addClientObserver(self, observer):
        """
        Add new observer for this protocol
        @param observer: new observer
        """
        self._clientObservers.append(observer)
        observer._clientListener = self
        
    def recvRectangle(self, rectangle, pixelFormat, data):
        """
        Receive rectangle order
        Main update order type
        @param rectangle: Rectangle type header of packet
        @param pixelFormat: pixelFormat struct of current session
        @param data: image data
        """
        for observer in self._clientObservers:
            observer.onUpdate(rectangle.width.value, rectangle.height.value, rectangle.x.value, rectangle.y.value, pixelFormat, rectangle.encoding, data)
    
    def sendKeyEvent(self, isDown, key):
        """
        Send a key event throw RFB protocol
        @param isDown: boolean notify if key is pressed or not (True if key is pressed)
        @param key: ASCII code of key
        """
        if not self._rfbLayer._ready:
            print "Try to send key event on non ready layer"
            return
        try:
            event = KeyEvent()
            event.downFlag.value = isDown
            event.key.value = key
        
            self._rfbLayer.sendKeyEvent(event)
        except InvalidValue:
            print "Try to send an invalid key event"
        
    def sendPointerEvent(self, mask, x, y):
        """
        Send a pointer event throw RFB protocol
        @param mask: mask of button if button 1 and 3 are pressed then mask is 00000101
        @param x: x coordinate of mouse pointer
        @param y: y pointer of mouse pointer
        """
        if not self._rfbLayer._ready:
            print "Try to send pointer event on non ready layer"
            return
        try:
            event = PointerEvent()
            event.mask.value = mask
            event.x.value = x
            event.y.value = y
            
            self._rfbLayer.sendPointerEvent(event)
        except InvalidValue:
            print "Try to send an invalid pointer event"
        

class ClientFactory(protocol.Factory):
    """
    Twisted Factory of RFB protocol
    """
    def buildProtocol(self, addr):
        """
        Function call by twisted on connection
        @param addr: address where client try to connect
        """
        controller = RFBController()
        self.buildObserver(controller)
        return controller.getRFBLayer()
    
    def buildObserver(self, controller):
        """
        Build an RFB observer object
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "buildObserver", "ClientFactory"))
    
        
class RFBClientObserver(object):
    """
    RFB client protocol observer
    """
    def __init__(self, controller):
        self._controller = controller
        self._controller.addClientObserver(self)
    
    def getController(self):
        """
        @return: RFB controller use by observer
        """
        return self._controller
        
    def keyEvent(self, isPressed, key):
        """
        Send a key event
        @param isPressed: state of key
        @param key: ASCII code of key
        """
        self._controller.sendKeyEvent(isPressed, key)
        
    def mouseEvent(self, button, x, y):
        """
        Send a mouse event to RFB Layer
        @param button: button number which is pressed (0,1,2,3,4,5,6,7,8)
        @param x: x coordinate of mouse pointer
        @param y: y coordinate of mouse pointer
        """
        mask = 0
        if button == 1:
            mask = 1
        elif button > 1:
            mask = 1 << button - 1
            
        self._controller.sendPointerEvent(mask, x, y)
        
    def onUpdate(self, width, height, x, y, pixelFormat, encoding, data):
        """
        Receive FrameBuffer update
        @param width : width of image
        @param height : height of image
        @param x : x position
        @param y : y position
        @param pixelFormat : pixel format struct from rfb.types
        @param encoding : encoding struct from rfb.types
        @param data : in respect of dataFormat and pixelFormat
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "onUpdate", "RFBClientObserver"))
