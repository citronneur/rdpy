'''
Created on 4 sept. 2013
@author: sylvain
'''
from PyQt4 import QtGui
from rdpy.protocol.rfb.observer import RfbObserver
from rdpy.protocol.network.type import UInt8

class QAdaptor(object):
    '''
    Adaptor for all qt
    '''
    def __init__(self):
        self._observers = []
        
    def addObserver(self, observer):
        self._observers.append(observer)
        
    def notifyImage(self, x, y, qimage):
        for observer in self._observers:
            observer.notifyImage(x, y, qimage)
        
    def sendMouseEvent(self, e):
        pass
    def sendKeyEvent(self, e):
        pass
    

class RfbAdaptor(RfbObserver, QAdaptor):
    '''
    classdocs
    '''
    
    def __init__(self, rfb):
        QAdaptor.__init__(self)
        self._rfb = rfb
        self._rfb.addObserver(self)
    
    def notifyFramebufferUpdate(self, width, height, x, y, pixelFormat, encoding, data):
        '''
        implement RfbAdaptor interface
        '''
        
        imageFormat = None
        if pixelFormat.BitsPerPixel == UInt8(32) and pixelFormat.RedShift == UInt8(16):
            imageFormat = QtGui.QImage.Format_RGB32
        else:
            print "Receive image in bad format"
            return
            
        image = QtGui.QImage(data, width.value, height.value, imageFormat)
        self.notifyImage(x.value, y.value, image)
        
    def sendMouseEvent(self, e):
        '''
        convert qt mouse event to rfb mouse event
        '''
        self._rfb.sendPointerEvent(0, e.pos().x(), e.pos().y())
        
    def sendKeyEvent(self, e):
        '''
        convert qt key press event to rfb press event
        '''
        self._rfb.sendKeyEvent(True, e.nativeVirtualKey())