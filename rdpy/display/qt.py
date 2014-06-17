'''
@author: sylvain
'''
from PyQt4 import QtGui, QtCore
from rdpy.protocol.rfb.rfb import RfbObserver

class QAdaptor(object):
    '''
    adaptor model with link beetween protocol
    and qt widget 
    '''
    def __init__(self):
        '''
        constructor
        must set qRemoteDesktop attribute
        '''
        #qwidget use for render
        self._qRemoteDesktop = None

    def sendMouseEvent(self, e):
        '''
        interface to send mouse event
        to protocol stack
        @param e: qEvent
        '''
        pass
    
    def sendKeyEvent(self, e):
        '''
        interface to send key event
        to protocol stack
        @param e: qEvent
        '''
        pass
    

class RfbAdaptor(RfbObserver, QAdaptor):
    '''
    QAdaptor for specific RFB protocol stack
    is to an RFB observer 
    '''
    def __init__(self, rfb):
        '''
        ctor
        @param rfb: RFB protocol stack
        '''
        self._rfb = rfb
        #set RFB observer to
        self._rfb.addObserver(self)
    
    def notifyFramebufferUpdate(self, width, height, x, y, pixelFormat, encoding, data):
        '''
        implement RfbAdaptor interface
        @param width: width of new image
        @param height: height of new image
        @param x: x position of new image
        @param y: y position of new image
        @param pixelFormat: pixefFormat structure in rfb.message.PixelFormat
        @param encoding: encoding type rfb.message.Encoding
        @param data: image data in accordance with pixelformat and encoding
        '''
        imageFormat = None
        if pixelFormat.BitsPerPixel.value == 32 and pixelFormat.RedShift.value == 16:
            imageFormat = QtGui.QImage.Format_RGB32
        else:
            print "Receive image in bad format"
            return
 
        image = QtGui.QImage(data, width, height, imageFormat)
        self._qRemoteDesktop.notifyImage(x, y, image)
        
    def sendMouseEvent(self, e):
        '''
        convert qt mouse event to rfb mouse event
        send mouse event to rfb protocol stack
        @param e: qMouseEvent
        '''
        button = e.button()
        mask = 0
        if button == QtCore.Qt.LeftButton:
            mask = 1
        elif button == QtCore.Qt.MidButton:
            mask = 1 << 1
        elif button == QtCore.Qt.RightButton:
            mask = 1 << 2   
        self._rfb.sendPointerEvent(mask, e.pos().x(), e.pos().y())
        
    def sendKeyEvent(self, e):
        '''
        convert qt key press event to rfb press event
        send key event to protocol stack
        @param e: qKeyEvent
        '''
        self._rfb.sendKeyEvent(True, e.nativeVirtualKey())

        
class QRemoteDesktop(QtGui.QWidget):
    '''
    qt display widget
    '''
    def __init__(self, adaptor):
        '''
        constructor
        @param adaptor: any object which inherit 
        from QAdaptor (RfbAdaptor | RdpAdaptor)
        '''
        super(QRemoteDesktop, self).__init__()
        #set adaptor
        self._adaptor = adaptor
        #set widget attribute of adaptor
        self._adaptor._qRemoteDesktop = self
        #refresh stack of image
        #because we can update image only in paint
        #event function. When protocol receive image
        #we will stock into refresh list
        #and in paiont event paint list of all refresh iomages
        self._refresh = []
        #bind mouse event
        self.setMouseTracking(True)
    
    def notifyImage(self, x, y, qimage):
        '''
        function call from Qadaptor
        @param x: x position of new image
        @param y: y position of new image
        @param qimage: new qimage
        '''
        #save in refresh list (order is important)
        self._refresh.append({"x" : x, "y" : y, "image" : qimage})
        #force update
        self.update()
        
    def paintEvent(self, e):
        '''
        call when QT renderer engine estimate that is needed
        @param e: qevent
        '''
        #if there is no refresh -> done
        if self._refresh == []:
            return
        #create painter to update background
        qp = QtGui.QPainter()
        #draw image
        qp.begin(self)
        for image in self._refresh:
            qp.drawImage(image["x"], image["y"], image["image"])
        qp.end()
        
        self._lastReceive = []
        
    def mouseMoveEvent(self, event):
        '''
        call when mouse move
        @param event: qMouseEvent
        '''
        self._adaptor.sendMouseEvent(event)
        
    def mousePressEvent(self, event):
        '''
        call when button mouse is pressed
        @param event: qMouseEvent
        '''
        self._adaptor.sendMouseEvent(event)
        
    def keyPressEvent(self, event):
        '''
        call when button key is pressed
        @param event: qKeyEvent
        '''
        self._adaptor.sendKeyEvent(event)