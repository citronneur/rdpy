'''
@author: sylvain
'''
from twisted.internet import protocol
from rdpy.network.error import CallPureVirtualFuntion, InvalidValue
import tpkt, tpdu, mcs, pdu

class RDPClientController(pdu.PDUClientListener):
    """
    use to decode and dispatch to observer PDU messages and orders
    """
    def __init__(self):
        """
        @param observer: observer
        """
        #list of observer
        self._clientObserver = []
        #transport layer
        self._pduLayer = pdu.PDU(self)
        
    def getPDULayer(self):
        """
        @return: PDU layer use by controller
        """
        return self._pduLayer
        
    def enablePerformanceSession(self):
        """
        Set particular flag in RDP stack to avoid wallpaper, theming, menu animation etc...
        """
        self._pduLayer._info.extendedInfo.performanceFlags.value = pdu.PerfFlag.PERF_DISABLE_WALLPAPER | pdu.PerfFlag.PERF_DISABLE_MENUANIMATIONS | pdu.PerfFlag.PERF_DISABLE_CURSOR_SHADOW | pdu.PerfFlag.PERF_DISABLE_THEMING
        
    def addClientObserver(self, observer):
        """
        add observer to RDP protocol
        @param observer: new observer to add
        """
        self._clientObserver.append(observer)
        observer._clientListener = self
        
    def recvBitmapUpdateDataPDU(self, rectangles):
        """
        call when a bitmap data is received from update PDU
        @param rectangles: [pdu.BitmapData] struct
        """
        for observer in self._clientObserver:
            #for each rectangle in update PDU
            for rectangle in rectangles:
                observer.onBitmapUpdate(rectangle.destLeft.value, rectangle.destTop.value, rectangle.destRight.value, rectangle.destBottom.value, rectangle.width.value, rectangle.height.value, rectangle.bitsPerPixel.value, rectangle.flags.value & pdu.BitmapFlag.BITMAP_COMPRESSION, rectangle.bitmapDataStream.value)
    
    def sendPointerEvent(self, x, y, button, isPressed):
        """
        send pointer events
        @param x: x position of pointer
        @param y: y position of pointer
        @param button: 1 or 2 or 3
        @param isPressed: true if button is pressed or false if it's released
        """
        if not self._pduLayer._isConnected:
            return

        try:
            event = pdu.PointerEvent()
            if isPressed:
                event.pointerFlags.value |= pdu.PointerFlag.PTRFLAGS_DOWN
            
            if button == 1:
                event.pointerFlags.value |= pdu.PointerFlag.PTRFLAGS_BUTTON1
            elif button == 2:
                event.pointerFlags.value |= pdu.PointerFlag.PTRFLAGS_BUTTON2
            elif button == 3:
                event.pointerFlags.value |= pdu.PointerFlag.PTRFLAGS_BUTTON3
            else:
                event.pointerFlags.value |= pdu.PointerFlag.PTRFLAGS_MOVE
            
            #position
            event.xPos.value = x
            event.yPos.value = y
            
            #send proper event
            self._pduLayer.sendInputEvents([event])
            
        except InvalidValue:
            print "try send pointer event with incorrect position"
            
    def sendKeyEventScancode(self, code, isPressed):
        """
        Send a scan code to RDP stack
        @param code: scan code
        @param isPressed: True if key is pressed and false if it's released
        """
        if not self._pduLayer._isConnected:
            return
        
        try:
            event = pdu.ScancodeKeyEvent()
            event.keyCode.value = code
            if isPressed:
                event.keyboardFlags.value |= pdu.KeyboardFlag.KBDFLAGS_DOWN
            else:
                event.keyboardFlags.value |= pdu.KeyboardFlag.KBDFLAGS_RELEASE
            
            #send event
            self._pduLayer.sendInputEvents([event])
            
        except InvalidValue:
            print "try send bad key event"
            
    def sendKeyEventUnicode(self, code, isPressed):
        """
        Send a scan code to RDP stack
        @param code: unicode
        @param isPressed: True if key is pressed and false if it's released
        """
        if not self._pduLayer._isConnected:
            return
        
        try:
            event = pdu.UnicodeKeyEvent()
            event.unicode.value = code
            if not isPressed:
                event.keyboardFlags.value |= pdu.KeyboardFlag.KBDFLAGS_RELEASE
            
            #send event
            self._pduLayer.sendInputEvents([event])
            
        except InvalidValue:
            print "try send bad key event"
                

class ClientFactory(protocol.Factory):
    """
    Factory of Client RDP protocol
    """
    def __init__(self, width = 1024, height = 800):
        """
        @param width: width of screen
        @param height: height of screen
        """
        self._width = width
        self._height = height
        
    def buildProtocol(self, addr):
        '''
        Function call from twisted and build rdp protocol stack
        @param addr: destination address
        '''
        controller = RDPClientController()
        self.buildObserver(controller)
        mcsLayer = mcs.createClient(controller)
        
        #set screen definition in MCS layer
        mcsLayer._clientSettings.core.desktopHeight.value = self._height
        mcsLayer._clientSettings.core.desktopWidth.value = self._width
        
        return tpkt.TPKT(tpdu.createClient(mcsLayer));
    
    def buildObserver(self, controller):
        '''
        build observer use for connection
        '''
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "buildObserver", "ClientFactory"))

class ServerFactory(protocol.Factory):
    '''
    Factory of Serrve RDP protocol
    '''
    def __init__(self, privateKeyFileName, certificateFileName):
        """
        @param privateKeyFileName: file contain server private key
        @param certficiateFileName: file that contain publi key
        """
        self._privateKeyFileName = privateKeyFileName
        self._certificateFileName = certificateFileName
        
    def buildProtocol(self, addr):
        """
        Function call from twisted and build rdp protocol stack
        @param addr: destination address
        """
        pduLayer = pdu.PDU(pdu.PDUServerListener())
        return tpkt.TPKT(tpdu.createServer(mcs.createServer(pduLayer), self._privateKeyFileName, self._certificateFileName));
    
    def buildObserver(self):
        '''
        build observer use for connection
        '''
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "buildObserver", "ServerFactory")) 
        
class RDPClientObserver(object):
    '''
    class use to inform all RDP event handle by RDPY
    '''
    def __init__(self, controller):
        """
        @param listener: RDP listener use to interact with protocol
        """
        self._controller = controller
        self._controller.addClientObserver(self)
        
        
    def onBitmapUpdate(self, destLeft, destTop, destRight, destBottom, width, height, bitsPerPixel, isCompress, data):
        '''
        notify bitmap update
        @param destLeft: xmin position
        @param destTop: ymin position
        @param destRight: xmax position because RDP can send bitmap with padding
        @param destBottom: ymax position because RDP can send bitmap with padding
        @param width: width of bitmap
        @param height: height of bitmap
        @param bitsPerPixel: number of bit per pixel
        @param isCompress: use RLE compression
        @param data: bitmap data
        '''
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "onBitmapUpdate", "RDPClientObserver")) 