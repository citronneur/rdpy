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
Qt specific code

QRemoteDesktop is a widget use for render in rdpy
"""

from PyQt4 import QtGui, QtCore
from rdpy.protocol.rfb.rfb import RFBClientObserver
from rdpy.protocol.rdp.rdp import RDPClientObserver

from rdpy.network.type import UInt16Le, Stream
import rle

class QAdaptor(object):
    '''
    adaptor model with link between protocol
    and qt widget 
    '''

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
    
    def getWidget(self):
        '''
        @return: widget use for render
        '''
        pass

class RFBClientQt(RFBClientObserver, QAdaptor):
    '''
    QAdaptor for specific RFB protocol stack
    is to an RFB observer 
    '''    
    def __init__(self, controller):
        """
        @param controller: controller for obser
        """
        RFBClientObserver.__init__(self, controller)
        self._widget = QRemoteDesktop(self)
        
    def getWidget(self):
        '''
        @return: widget use for render
        '''
        return self._widget
    
    def onUpdate(self, width, height, x, y, pixelFormat, encoding, data):
        '''
        implement RFBClientObserver interface
        @param width: width of new image
        @param height: height of new image
        @param x: x position of new image
        @param y: y position of new image
        @param pixelFormat: pixefFormat structure in rfb.message.PixelFormat
        @param encoding: encoding type rfb.message.Encoding
        @param data: image data in accordance with pixel format and encoding
        '''
        imageFormat = None
        if pixelFormat.BitsPerPixel.value == 32 and pixelFormat.RedShift.value == 16:
            imageFormat = QtGui.QImage.Format_RGB32
        else:
            print "Receive image in bad format"
            return
 
        image = QtGui.QImage(data, width, height, imageFormat)
        self._widget.notifyImage(x, y, image)
        
    def sendMouseEvent(self, e):
        '''
        convert qt mouse event to RFB mouse event
        @param e: qMouseEvent
        '''
        button = e.button()
        buttonNumber = 0
        if button == QtCore.Qt.LeftButton:
            buttonNumber = 1
        elif button == QtCore.Qt.MidButton:
            buttonNumber = 2
        elif button == QtCore.Qt.RightButton:
            buttonNumber = 3  
        self.mouseEvent(buttonNumber, e.pos().x(), e.pos().y())
        
    def sendKeyEvent(self, e):
        '''
        convert Qt key press event to RFB press event
        @param e: qKeyEvent
        '''
        self.keyEvent(True, e.nativeVirtualKey())
        
class RDPClientQt(RDPClientObserver, QAdaptor):
    '''
    Adaptor for RDP client
    '''
    def __init__(self, controller):
        """
        @param controller: RDP controller
        """
        RDPClientObserver.__init__(self, controller)
        self._widget = QRemoteDesktop(self)
        
    def getWidget(self):
        '''
        @return: widget use for render
        '''
        return self._widget
    
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
        #TODO
        if isCompress:
            #rle.decode("", Stream(data), width, height, UInt16Le)
            return
        
        imageFormat = None
        if bitsPerPixel == 16:
            imageFormat = QtGui.QImage.Format_RGB16
        elif bitsPerPixel == 24:
            imageFormat = QtGui.QImage.Format_RGB888
        elif bitsPerPixel == 32:
            imageFormat = QtGui.QImage.Format_RGB32
        else:
            print "Receive image in bad format"
            return
        
        image = QtGui.QImage(data, width, height, imageFormat)
        self._widget.notifyImage(destLeft, destTop, image)

        
class QRemoteDesktop(QtGui.QWidget):
    '''
    qt display widget
    '''
    def __init__(self, adaptor):
        '''
        constructor
        '''
        super(QRemoteDesktop, self).__init__()
        #adaptor use to send
        self._adaptor = adaptor
        #refresh stack of image
        #because we can update image only in paint
        #event function. When protocol receive image
        #we will stock into refresh list
        #and in paiont event paint list of all refresh images
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
        if self._adaptor is None:
            print "No adaptor to send mouse move event"
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
        