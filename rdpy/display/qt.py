'''
@author: sylvain
'''
from PyQt4 import QtGui
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
        @param x: xpositionof new image
        @param y: y position of new image
        @param pixelFormat: pixefFormat structure in rfb.message.PixelFormat
        @param encoding: encoding typpe rfb.message.Encoding
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
        @param e: qEvent
        '''
        self._rfb.sendPointerEvent(0, e.pos().x(), e.pos().y())
        
    def sendKeyEvent(self, e):
        '''
        convert qt key press event to rfb press event
        send key event to protocol stack
        @param e: qevent
        '''
        self._rfb.sendKeyEvent(True, e.nativeVirtualKey())

        
class QRemoteDesktop(QtGui.QWidget):
    '''
    Class that represent the main
    widget
    '''
    def __init__(self, adaptor):
        super(QRemoteDesktop, self).__init__()
        self._adaptor = adaptor
        self._adaptor._qRemoteDesktop = self
        self._refresh = []
        self.setMouseTracking(True)
    
    def notifyImage(self, x, y, qimage):
        self._refresh.append({"x" : x, "y" : y, "image" : qimage})
        self.update()
        
    def paintEvent(self, e):
        if self._refresh == []:
            return
        qp = QtGui.QPainter()
        qp.begin(self)
        for image in self._refresh:
            qp.drawImage(image["x"], image["y"], image["image"])
        qp.end()
        
        self._lastReceive = []
        
    def mouseMoveEvent(self, event):
        self._adaptor.sendMouseEvent(event)

    def keyPressEvent(self, event):
        self._adaptor.sendKeyEvent(event)