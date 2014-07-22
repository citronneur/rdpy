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
from rdpy.base.error import CallPureVirtualFuntion

import rdpy.base.log as log

try:
    import rdpy.core.rle as rle
except:
    log.error("Please build core package before using RLE algorithm : scons -C rdpy/core install")


class QAdaptor(object):
    """
    Adaptor model with link between protocol
    And Qt widget 
    """
    def sendMouseEvent(self, e, isPressed):
        """
        Interface to send mouse event to protocol stack
        @param e: QMouseEvent
        @param isPressed: event come from press or release action
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "sendMouseEvent", "QAdaptor")) 
        
    def sendKeyEvent(self, e, isPressed):
        """
        Interface to send key event to protocol stack
        @param e: QEvent
        @param isPressed: event come from press or release action
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "sendKeyEvent", "QAdaptor")) 
    
    def getWidget(self):
        """
        @return: widget use for render
        """
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "getWidget", "QAdaptor"))
    
    def closeEvent(self, e):
        """
        Call when you want to close connection
        @param: QCloseEvent
        """ 
        raise CallPureVirtualFuntion("%s:%s defined by interface %s"%(self.__class__, "closeEvent", "QAdaptor"))
    
class RFBClientQt(RFBClientObserver, QAdaptor):
    """
    QAdaptor for specific RFB protocol stack
    is to an RFB observer 
    """   
    def __init__(self, controller, width, height):
        """
        @param controller: controller for observer
        @param width: width of widget
        @param height: height of widget
        """
        RFBClientObserver.__init__(self, controller)
        self._widget = QRemoteDesktop(self, width, height)
        
    def getWidget(self):
        """
        @return: widget use for render
        """
        return self._widget
    
    def onUpdate(self, width, height, x, y, pixelFormat, encoding, data):
        """
        Implement RFBClientObserver interface
        @param width: width of new image
        @param height: height of new image
        @param x: x position of new image
        @param y: y position of new image
        @param pixelFormat: pixefFormat structure in rfb.message.PixelFormat
        @param encoding: encoding type rfb.message.Encoding
        @param data: image data in accordance with pixel format and encoding
        """
        imageFormat = None
        if pixelFormat.BitsPerPixel.value == 32 and pixelFormat.RedShift.value == 16:
            imageFormat = QtGui.QImage.Format_RGB32
        else:
            log.error("Receive image in bad format")
            return
 
        image = QtGui.QImage(data, width, height, imageFormat)
        self._widget.notifyImage(x, y, image)
        
    def sendMouseEvent(self, e, isPressed):
        """
        Convert Qt mouse event to RFB mouse event
        @param e: qMouseEvent
        @param isPressed: event come from press or release action
        """
        button = e.button()
        buttonNumber = 0
        if button == QtCore.Qt.LeftButton:
            buttonNumber = 1
        elif button == QtCore.Qt.MidButton:
            buttonNumber = 2
        elif button == QtCore.Qt.RightButton:
            buttonNumber = 3  
        self.mouseEvent(buttonNumber, e.pos().x(), e.pos().y())
        
    def sendKeyEvent(self, e, isPressed):
        """
        Convert Qt key press event to RFB press event
        @param e: qKeyEvent
        @param isPressed: event come from press or release action
        """
        self.keyEvent(isPressed, e.nativeVirtualKey())

   
class RDPClientQt(RDPClientObserver, QAdaptor):
    """
    Adaptor for RDP client
    """
    def __init__(self, controller, width, height):
        """
        @param controller: RDP controller
        @param width: width of widget
        @param height: height of widget
        """
        RDPClientObserver.__init__(self, controller)
        self._widget = QRemoteDesktop(self, width, height)
        #set widget screen to RDP stack
        controller.setScreen(width, height)
        
    def getWidget(self):
        """
        @return: widget use for render
        """
        return self._widget
    
    def sendMouseEvent(self, e, isPressed):
        """
        Convert Qt mouse event to RDP mouse event
        @param e: qMouseEvent
        @param isPressed: event come from press(true) or release(false) action
        """
        button = e.button()
        buttonNumber = 0
        if button == QtCore.Qt.LeftButton:
            buttonNumber = 1
        elif button == QtCore.Qt.MidButton:
            buttonNumber = 2
        elif button == QtCore.Qt.RightButton:
            buttonNumber = 3  
        self._controller.sendPointerEvent(e.pos().x(), e.pos().y(), buttonNumber, isPressed)
        
    def sendKeyEvent(self, e, isPressed):
        """
        Convert Qt key press event to RFB press event
        @param e: QKeyEvent
        @param isPressed: event come from press or release action
        """
        self._controller.sendKeyEventUnicode(ord(unicode(e.text().toUtf8(), encoding="UTF-8")), isPressed)
    
    def closeEvent(self, e):
        """
        Convert Qt close widget event into close stack event
        @param e: QCloseEvent
        """
        self._controller.close()
    
    def onUpdate(self, destLeft, destTop, destRight, destBottom, width, height, bitsPerPixel, isCompress, data):
        """
        Notify bitmap update
        @param destLeft: xmin position
        @param destTop: ymin position
        @param destRight: xmax position because RDP can send bitmap with padding
        @param destBottom: ymax position because RDP can send bitmap with padding
        @param width: width of bitmap
        @param height: height of bitmap
        @param bitsPerPixel: number of bit per pixel
        @param isCompress: use RLE compression
        @param data: bitmap data
        """
        image = None
        if bitsPerPixel == 15:
            if isCompress:
                image = QtGui.QImage(width, height, QtGui.QImage.Format_RGB555)
                data = rle.bitmap_decompress(image.bits(), width, height, data, len(data), 2)
            else:
                image = QtGui.QImage(data, width, height, QtGui.QImage.Format_RGB555)
        
        elif bitsPerPixel == 16:
            if isCompress:
                image = QtGui.QImage(width, height, QtGui.QImage.Format_RGB16)
                data = rle.bitmap_decompress(image.bits(), width, height, data, len(data), 2)
            else:
                image = QtGui.QImage(data, width, height, QtGui.QImage.Format_RGB16)
        
        elif bitsPerPixel == 24:
            if isCompress:
                image = QtGui.QImage(width, height, QtGui.QImage.Format_RGB24)
                data = rle.bitmap_decompress(image.bits(), width, height, data, len(data), 3)
            else:
                image = QtGui.QImage(data, width, height, QtGui.QImage.Format_RGB24)
                
        elif bitsPerPixel == 32:
            if isCompress:
                image = QtGui.QImage(width, height, QtGui.QImage.Format_RGB32)
                data = rle.bitmap_decompress(image.bits(), width, height, data, len(data), 4)
            else:
                image = QtGui.QImage(data, width, height, QtGui.QImage.Format_RGB32)
        else:
            log.error("Receive image in bad format")
            return
        
        #if image need to be cut
        #For bit alignement server may send more than image pixel
        if width != destRight - destLeft + 1 or height != destBottom - destTop + 1:
            image = image.copy(0, 0, destRight - destLeft + 1, destBottom - destTop + 1)
        self._widget.notifyImage(destLeft, destTop, image)
    
    def onReady(self):
        """
        Call when stack is ready
        """
        #do something maybe a loader
        pass

        
class QRemoteDesktop(QtGui.QWidget):
    """
    Qt display widget
    """
    def __init__(self, adaptor, width, height):
        """
        @param adaptor: QAdaptor
        """
        super(QRemoteDesktop, self).__init__()
        #adaptor use to send
        self._adaptor = adaptor
        #set correct size
        self.resize(width, height)
        #refresh stack of image
        #because we can update image only in paint
        #event function. When protocol receive image
        #we will stock into refresh list
        #and in paint event paint list of all refresh images
        self._refresh = []
        #bind mouse event
        self.setMouseTracking(True)
        #buffer image
        self._buffer = QtGui.QImage(width, height, QtGui.QImage.Format_RGB32)
    
    def notifyImage(self, x, y, qimage):
        """
        Function call from QAdaptor
        @param x: x position of new image
        @param y: y position of new image
        @param qimage: new QImage
        """
        #save in refresh list (order is important)
        self._refresh.append({"x" : x, "y" : y, "image" : qimage})
        #force update
        self.update()
        
    def paintEvent(self, e):
        """
        Call when Qt renderer engine estimate that is needed
        @param e: QEvent
        """
        #if there is no refresh -> done
        if self._refresh == []:
            return
        #fill buffer image
        with QtGui.QPainter(self._buffer) as qp:
        #draw image
            for image in self._refresh:
                qp.drawImage(image["x"], image["y"], image["image"])
        #draw in widget
        with QtGui.QPainter(self) as qp:
            qp.drawImage(0, 0, self._buffer)
        self._refresh = []
        
    def mouseMoveEvent(self, event):
        """
        Call when mouse move
        @param event: QMouseEvent
        """
        self._adaptor.sendMouseEvent(event, False)
        
    def mousePressEvent(self, event):
        """
        Call when button mouse is pressed
        @param event: QMouseEvent
        """
        self._adaptor.sendMouseEvent(event, True)
        
    def mouseReleaseEvent(self, event):
        """
        Call when button mouse is released
        @param event: QMouseEvent
        """
        self._adaptor.sendMouseEvent(event, False)
        
    def keyPressEvent(self, event):
        """
        Call when button key is pressed
        @param event: QKeyEvent
        """
        self._adaptor.sendKeyEvent(event, True)
        
    def keyReleaseEvent(self, event):
        """
        Call when button key is released
        @param event: QKeyEvent
        """
        self._adaptor.sendKeyEvent(event, False)
        
    def closeEvent(self, event):
        """
        Call when widget is closed
        @param event: QCloseEvent
        """
        self._adaptor.closeEvent(event)